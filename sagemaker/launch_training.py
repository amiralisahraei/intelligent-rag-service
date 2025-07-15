from sagemaker.huggingface import HuggingFace, HuggingFaceModel
import sagemaker
import os

role = "arn:aws:iam::038462775601:role/service-role/AmazonSageMaker-ExecutionRole-20250303T193580"  # Replace with your actual ARN
sess = sagemaker.Session()

# Configure the estimator
huggingface_estimator = HuggingFace(
    entry_point='train.py',
    source_dir='sagemeker',
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


# Create HuggingFace Model class
huggingface_model = HuggingFaceModel(
    model_data=huggingface_estimator.model_data,  # Path to your trained model artifacts
    role=role,                                    # IAM role with permissions to create endpoint
    transformers_version='4.37.0',
    pytorch_version='2.1.0',
    py_version='py310',
    model_server_workers=1                        # Number of worker processes
)


# Deploy the model to an endpoint
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.2xlarge",  # Choose an appropriate instance type
    # endpoint_name="my-llm-endpoint"  # Specify a unique endpoint name
)

print("Model deployed to endpoint successfully!")
print(f"Endpoint name: {predictor.endpoint_name}")

# Output the endpoint name to a file that GitHub Actions can read
with open("endpoint_name.txt", "w") as f:
    f.write(predictor.endpoint_name)