import os
import json
import boto3
import cv2
import tempfile
import base64
import time
from typing import List, Dict, Any, Tuple, Optional



class VideoFrameExtractor:
    """Extracts frames from video files at regular intervals."""
    
    def __init__(self):
        pass
    
    def extract_frames(self, video_path: str, max_frames: int = 20) -> List[str]:
        """
        Extract frames from the video at regular intervals.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of paths to extracted frame images
        """
        print("Extracting frame from the video... ")
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval to get max_frames evenly distributed frames
        frame_interval = max(total_frames // max_frames, 1)
        
        frames_dir = tempfile.mkdtemp()
        extracted_frames = []
        
        frame_positions = range(0, total_frames, frame_interval)[:max_frames]
        
        for frame_pos in frame_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            success, frame = cap.read()
            if success:
                frame_path = os.path.join(frames_dir, f"frame_{frame_pos}.jpg")
                cv2.imwrite(frame_path, frame)
                extracted_frames.append(frame_path)
        
        cap.release()
        return extracted_frames


class ClaudeAnalyzer:
    """Analyzes video frames using Claude via Amazon Bedrock."""
    
    def __init__(self, compliance_session ):
        """
        Initialize the Claude analyzer.
        
        Args:
            model_id: Claude model ID to use for analysis
        """
        self.bedrock_client = compliance_session.client('bedrock-runtime')
    
    def analyze_frames(self, frame_paths: List[str], prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Analyze all frames together using Claude via Amazon Bedrock.
        
        Args:
            frame_paths: List of paths to frame images
            prompt: The compliance question/prompt to analyze against
            max_retries: Maximum number of retry attempts on failure
            
        Returns:
            Dictionary containing analysis results and compliance status
        """
        print("Analysing video frames and generating report ... ")
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Prepare all images
                image_contents = []
                for image_path in frame_paths:
                    with open(image_path, "rb") as img_file:
                        image_bytes = img_file.read()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        image_contents.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        })

                # Construct the message for Claude with all frames
                message_content = [{
                    "type": "text",
                    "text": f"""Please analyze these {len(frame_paths)} frames from a video for the following compliance question: {prompt}

                                Please provide:
                                1. A comprehensive analysis considering all frames together
                                2. A clear assessment of whether the video shows overall compliance or non-compliance with the requirement
                                3. Key observations that led to your conclusion
                                4. Any additional context or information that supports your analysis
                                5. Do not mention numbers of frames or individual frames in your response.

                                Combine your analysis into a single, coherent response."""
                }]
                message_content.extend(image_contents)

                messages = [{
                    "role": "user",
                    "content": message_content
                }]

                # Call Claude via Bedrock
                response = self.bedrock_client.invoke_model(
                    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                    contentType =  "application/json",
                    accept = "application/json",
                    body=json.dumps({
                        "messages": messages,
                        "max_tokens": 1000,
                        "anthropic_version": "bedrock-2023-05-31"
                    }),
                )

                # Parse the response
                response_body = json.loads(response['body'].read().decode('utf-8'))
                analysis = response_body['content'][0]['text']

                # Determine compliance from the combined analysis
                is_compliant = (
                    "compliant" in analysis.lower() and 
                    "non-compliant" not in analysis.lower()
                )

                return {
                    "combined_analysis": analysis,
                    "compliant": is_compliant
                }

            except Exception as e:
                print(f"Error analyzing frames (Attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    return {
                        "combined_analysis": f"Error analyzing frames after {max_retries} attempts: {str(e)}",
                        "compliant": False
                    }
                time.sleep(2)  # Wait before retrying


class ComplianceChecker:
    """Main class for checking video compliance using Claude."""
    
    def __init__(self ):
        """
        Initialize the compliance checker.
        
        Args:
            model_id: Claude model ID to use for analysis
            upload_folder: Directory to store uploaded files
        """
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.compliance_session = boto3.session.Session(
                region_name=self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
        )
        self.frame_extractor = VideoFrameExtractor()
        self.analyzer = ClaudeAnalyzer(self.compliance_session)
    
    def check_compliance(self, video_file: str, prompt: str) -> Tuple[Dict[str, Any], Optional[int]]:
        """
        Process video frames and check compliance using Claude.
        
        Args:
            video_file: Path to the video file to analyze
            prompt: The compliance question/prompt
            
        Returns:
            Tuple of (result_dict, status_code) where status_code is optional
        """
        print("Starting Health Compliance Process...")
        try:
            # Extract frames
            frames = self.frame_extractor.extract_frames(video_file)
            if not frames:
                return {"error": "No frames could be extracted from the video"}, 500
            
            # Analyze all frames together
            analysis_result = self.analyzer.analyze_frames(frames, prompt)
            print("Analysis Complete ! ")
            return {
                "analysis": analysis_result["combined_analysis"],
                "compliant": analysis_result["compliant"]
            }, None

        except Exception as e:
            return {"error": str(e)}, 500

