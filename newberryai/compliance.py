import os
import json
import boto3
import cv2
import tempfile
import base64
import time
from newberryai.aws_auth import config  # Import the config function

# Use the config function to set up the Bedrock client
bedrock_client = config(service='bedrock')  # For Claude via Bedrock

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_frames(video_path, max_frames=20):
    """
    Extract frames from the video at regular intervals.
    Returns a list of frame file paths.
    """
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

def analyze_frames_with_claude(frame_paths, prompt, max_retries=3):
    """
    Analyze all frames together using Claude via Amazon Bedrock.
    Returns a combined analysis.
    """
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
            response = bedrock_client.invoke_model(
                modelId="arn:aws:bedrock:us-east-2:535002855311:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0",
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

def check_compliance(video_file: str, prompt: str):
    """
    Process video frames and check compliance using Claude.
    """
    try:
        # Extract frames
        frames = extract_frames(video_file)
        if not frames:
            return {"error": "No frames could be extracted from the video"}, 500
        
        # Analyze all frames together
        analysis_result = analyze_frames_with_claude(frames, prompt)
        
        return {
            "analysis": analysis_result["combined_analysis"],
            "compliant": analysis_result["compliant"]
        }

    except Exception as e:
        return {"error": str(e)}, 500
