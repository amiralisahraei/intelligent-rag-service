from sagemaker.huggingface import HuggingFace
import sagemaker

role = "arn:aws:iam::038462775601:role/service-role/AmazonSageMaker-ExecutionRole-20250303T193580"  # Replace with your actual ARN
sess = sagemaker.Session()

# Create a dummy file for input_data requirement
# with open('dummy.txt', 'w') as f:
#     f.write('This is a dummy file for SageMaker input requirement')

# Upload dummy file to S3
# bucket = sess.default_bucket()
# dummy_s3_path = sess.upload_data(path='dummy.txt', bucket=bucket, key_prefix='dummy')

# Configure the estimator
huggingface_estimator = HuggingFace(
    entry_point='train.py',
    source_dir='.',
    instance_type='ml.g5.2xlarge',
    instance_count=1,
    role=role,
    transformers_version='4.36.0',
    pytorch_version='2.1.0',
    py_version='py310',
    environment={
        'HUGGINGFACE_HUB_CACHE': '/tmp/.cache',  # Optional: cache location
    }
)

# Use dummy S3 path (your script will ignore this and use HF Hub)
input_data = {'train': "s3://llm-fine-tuning-amirkahn/dummy/dummy.txt"}  # Replace with your actual S3 path if needed

# Start training
print("Starting SageMaker training job...")
huggingface_estimator.fit(input_data)

print("Training job completed!")
print(f"Model artifacts: {huggingface_estimator.model_data}")