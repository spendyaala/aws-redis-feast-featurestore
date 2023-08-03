## Redis Enterprise Cloud as a Online Feature Store on AWS

This repo showcases proof of value of leveraging Redis Enterprise Cloud as a Feature Store.
We will use open source [Feast](https://feast.dev/) as the Online Feature Store, that uses Redis Enterprise Cloud as the datastore, to store features.

## What are we building?

I will explain it later. `TBD`

## About Redis Enterprise Cloud

I will explain it later. `TBD`

## About Amazon Redshift, Glue, S3

I will explain it later. `TBD`

## Pre-requisites
- Terraform
- Git
- Python Dev toolkit
- AWS Account with sufficient previleges
- AWS CLI configured to access your AWS account.



## Setup
1. Get an EC2 machine running Amazon Linux ( example:  `ami-0507f77897697c4ba` in `us-west-2` region).
2. Install Terraform, Git, Python dev toolkit.
Typical instructions for an Amazon Linux EC2 machine may look like this:

### Terraform
```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo

sudo yum -y install terraform

terraform -help
terraform -help plan
```

### Git
```
sudo yum install git -y
```

If you are big fan of using github CLI, you can install it by following installation instructions for `Amazon Linux` at this [link here](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).

### Python Dev toolkit

```
sudo yum groupinstall "Development Tools" -y
python3 -m pip install --upgrade pip
sudo yum install python3-devel -y
```

3. Configure AWS CLI.
```
aws configure
```
This will prompt you to enter the following configuration parameters. You need to enter these values.
- aws_access_key_id
- aws_secret_access_key
- region_name

Typical example values for the above configuration parameters. Please do not use these values as they are. They are just an example to help you understand how real values may look like:
```
aws_access_key_id     = AKIA2KWUDBSDIG3YNDGK
aws_secret_access_key = 8PgCIMAnbBOX4JP97TNTX7mOcrUK3D0Xo9Eqnsd$
region_name           = us-west-2
```

## Amazon Redshift as your Offline Feature Store
1. Now we will setup Offline Feature Store. We will use Amazon Redshift as our offline feature store. We will also use S3 as an object store for housing raw data.

2. Let us start with Terraform. We will deploy Redshift, an S3 bucket containing zipcode and credit history parquet files, using Terraform. We will also setup required IAM roles and policies for Redshift to access S3, and create a Redshift table that can query the parquet files.

```
cd setup\terraform
terraform init

```
Now initialize a few Terraform variables. We will use these for setting up featurestore at a later point of time.

```
export TF_VAR_region="us-west-2"
export TF_VAR_project_name="your-project-name"
export TF_VAR_admin_password="$(openssl rand -base64 32)"
```
Examine the Terraform explain
```
terraform plan
```
If everything looks good, go ahead and deploy the infra.

```
terraform apply
```

If your infrastructure is deployed successfully, at the end, you should see the following outputs from Terraform

```
redshift_cluster_identifier = "my-feast-project-redshift-cluster"
redshift_spectrum_arn = "arn:aws:iam::<Account>:role/s3_spectrum_role"
credit_history_table = "credit_history"
zipcode_features_table = "zipcode_features"
```
Please make a note of these values, as you would use them later.

3. Next we create an external Glue tables in Redshift cluster to point to the external catalog data in S3.

```
aws redshift-data execute-statement \
    --region "${TF_VAR_region}" \
    --cluster-identifier "${tf_redshift_cluster_identifier}" \
    --db-user admin \
    --database dev \
    --sql "create external schema spectrum from data catalog database 'dev' iam_role '${tf_redshift_spectrum_arn}' create external database if not exists;"
```

4. Verify if the command was successful or not by running the following command. Please substitute your statement id found from above command.
```
aws redshift-data describe-statement --id [SET YOUR STATEMENT ID HERE]
```

5. Now you can query the actual zipcode features by running the following command.
```
aws redshift-data execute-statement \
    --region "${TF_VAR_region}" \
    --cluster-identifier "${tf_redshift_cluster_identifier}" \
    --db-user admin \
    --database dev \
    --sql "SELECT * from spectrum.zipcode_features LIMIT 1;"
```

6. If you would like to print out the results, you can run the following statement.
```
aws redshift-data get-statement-result --id [SET YOUR STATEMENT ID HERE]
```

## Setting up Redis Enterprise Cloud

Its time to deply Redis Enterprise Cloud on AWS, by going to the web application portal: https://app.redislabs.com.

You can choose to deploy a Fixed or Flexible deployment. After you provision a fully managed DBaaS(Database-as-a-Service) from Redis, please take a note of the following database endpoint configurations.
- Redis Database Server hostname.
- Redis Database Server Port number.
- Redis Database Server Default user password.

Example settings:
```
Redis Database Server hostname: redis-15764.c259.us-east-1-2.ec2.cloud.redislabs.com
Redis Database Server port#: 15764
Redis Database Server user: default
Redis Database Server Password: hVxPhlEBp5c6JopAKJCNUIwNoGttSPCF```
```
You will need above details to configure Feast to leverage your Redis Enterprise Cloud on AWS.

## Configuring Online Feature Store with Feast and Redis
1. Lets clone this git repo.
```
git clone https://github.com/spendyaala/aws-redis-feast-featurestore.git
```

OR if you are using the github CLI:
```
gh repo clone spendyaala/aws-redis-feast-featurestore
```

2. Lets create a Python virtual environment. We will install all python dependencies within this virtual environment.

```
cd aws-redis-feast-featurestore
python3 -m venv redis-aws-feast.venv
source redis-aws-feast.venv/bin/activate
```

3. Now let us setup Feast. Feast will be our Feature Store and it will leverage Redis Enterprise Cloud as its datastore. We will install feast with AWS and Redis dependencies.

```
 pip install 'feast[redis,aws]==0.31.1'
```

4. Install a few python dependencies
```
pip3 install -r setup/requirements.txt
```

5. In general we usually setup a feature repository after you install `feast` with `redis` and `aws` dependencies in the previous step. However, in this case, we have already setup a feature repository in [feature_repo/](feature_repo/) folder. So there is no necessity of creating a new feature repository again. So, we will skip running a typical command `feast init -t aws feature_repo` deliberately.

Since we don't need to `init` a new repository, all we have to do is configure the
[feature_store.yaml/](feature_repo/feature_store.yaml) in the feature repository. Please set the fields under
`offline_store` to the configuration you have received when deploying your Redshift cluster and S3 bucket.

Edit the `feature_store.yaml` file and replace all the configurations that starts with `<replace-this-with-` with actual values.

```
cd feature_repo
vi feature_store.yaml
```

6. Deploy the feature store by running `apply` from within the `feature_repo/` folder
```
cd feature_repo/
feast apply
```
You would see the following text displayed in the output of the command above.
```
Registered entity dob_ssn
Registered entity zipcode
Registered feature view credit_history
Registered feature view zipcode_features
Deploying infrastructure for credit_history
Deploying infrastructure for zipcode_features
```

7. Next we load features into the online store using the `materialize-incremental` command. This command will load the latest feature values from a data source into the online store.

```
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
feast materialize-incremental $CURRENT_TIME
```

## Training and testing the model.
We train the model using a combination of loan data from S3 and our zipcode and credit history features from Redshift (which in turn queries S3), and then we test online inference by reading those same features from online feature store : Redis Enterprise Cloud.

```
cd codebase
python run.py
```
The script should then output the result of a single loan application. This may take anywhere between 2 to 3 minutes, as the code also trains on the data, before making a prediction.
```
loan rejected!
```

## Interactive Real-time Web app in action
Finally lest run a web up that demonstrates interactively retrieving the online features from Redis in realtime and makes inferencing against the deployed model. This interactive demo is based on Streamlit application.

Start the Streamlit application, using the following command.
```
cd codebase
streamlit run streamlit_app.py
```
Then navigate to the URL on which Streamlit is being served. You should see a user interface through which loan applications can be made.

The output may look like this:
```
streamlit run streamlit_app.py

Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.


  You can now view your Streamlit app in your browser.

  Network URL: http://172.31.6.9:8501
  External URL: http://52.36.34.145:8501

```

Simply fire up a browser and navigate to the External URL mentioned above.
If you are running this on an EC2 instance, you may need to setup appropriate security group configurations like this: (Please note these configurations are not meant for Production workloads.)

![Security Group Config](./setup/security-group-config.png)

If everything goes well, you will see the web application coming up in your browser.
![Web App](./setup/webapp.png)
