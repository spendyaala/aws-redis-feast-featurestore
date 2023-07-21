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

4. Now we will setup Offline Feature Store. We will use Amazon Redshift as our offline feature store. We will also use S3 as an object store for housing raw data.

5. Let us start with Terraform. We will deploy Redshift, an S3 bucket containing zipcode and credit history parquet files, using Terraform. We will also setup required IAM roles and policies for Redshift to access S3, and create a Redshift table that can query the parquet files.

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

6. Next we create an external Glue tables in Redshift cluster to point to the external catalog data in S3.

```
aws redshift-data execute-statement \
    --region "${TF_VAR_region}" \
    --cluster-identifier "${tf_redshift_cluster_identifier}" \
    --db-user admin \
    --database dev \
    --sql "create external schema spectrum from data catalog database 'dev' iam_role '${tf_redshift_spectrum_arn}' create external database if not exists;"
```

7. Verify if the command was successful or not by running the following command. Please substitute your statement id found from above command.
```
aws redshift-data describe-statement --id [SET YOUR STATEMENT ID HERE]
```

8. Now you can query the actual zipcode features by running the following command.
```
aws redshift-data execute-statement \
    --region "${TF_VAR_region}" \
    --cluster-identifier "${tf_redshift_cluster_identifier}" \
    --db-user admin \
    --database dev \
    --sql "SELECT * from spectrum.zipcode_features LIMIT 1;"
```

9. If you would like to print out the results, you can run the following statement.
```
aws redshift-data get-statement-result --id [SET YOUR STATEMENT ID HERE]
```

10. Lets create a Python virtual environment. We will install all python dependencies within this virtual environment.

```
python3 -m venv redis-aws-feast.venv
source redis-aws-feast.venv/bin/activate
```


10. Now let us setup Feast. Feast will be our Feature Store and it will leverage Redis Enterprise Cloud as its datastore. We will install feast with AWS and Redis dependencies.

```
 pip install 'feast[redis,aws]'
```

11. In general we usually setup a feature repository after you install `feast` with `redis` and `aws` dependencies in the previous step. However, in this case, we have already setup a feature repository in [feature_repo/](feature_repo/) folder. So there is no necessity of creating a new feature repository again. So, we will skip running a typical command `feast init -t aws feature_repo` deliberately.

Since we don't need to `init` a new repository, all we have to do is configure the
[feature_store.yaml/](feature_repo/feature_store.yaml) in the feature repository. Please set the fields under
`offline_store` to the configuration you have received when deploying your Redshift cluster and S3 bucket.
