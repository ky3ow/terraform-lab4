# Introduction

This is repository for cloud lab work #4, it involves provisioning serverless python API via **AWS API Gateway** and **AWS Lambda**

# Structure

```
.
├── envs/            # root terraform modules for each environment
│   └── dev/
├── modules/         # reusable terrform modules
│   ├── api_gateway/
│   ├── bucket/
│   ├── dynamodb/
│   └── lambda/
└── src/             # python code which will run on lambda
```

# Prerequisites

- aws account
- aws cli installed
- bucket for remote state provisioned

# How to run

`terraform init && terraform apply` to provision the infra

```bash
api_url="$(terraform output -raw api_url)"

curl -X POST "$api_url/notes" \
     -H "Content-Type: application/json" \
     -d '{"text": "your note text"}'   # create a note

curl -X GET "$api_url/notes/noteId"    # get a note
curl -X DELETE "$api_url/notes/noteId" # delete a note
```
