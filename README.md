# Introduction

This is repository for cloud lab work #4-5, it involves provisioning serverless python API via **AWS API Gateway** and **AWS Lambda**

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
├── src/             # python code which will run on lambda
├── build/           # generated on build(bundling python deps for lambda layer)
└── build.sh         # small build script to bundle python deps
```

# Prerequisites

- aws account
- aws cli installed
- bucket for remote state provisioned
- uv for python
- curl for testing
  - jq for curl result formatting

# How to run

First run `./build.sh` to generate bundle of python dependencies for lambda layer

`terraform init && terraform apply` to provision the infra

```bash
# general
api_url="$(terraform output -raw api_url)"

curl -X POST "$api_url/notes" \
     -H "Content-Type: application/json" \
     -d '{"text": "your note text"}'        # create a note

curl -X GET "$api_url/notes/noteId"         # get a note
curl -X DELETE "$api_url/notes/noteId"      # delete a note

curl -X GET "$api_url/notes/noteId/phrases" # get key phrases from a note
```

```bash
# full note lifecycle

note_id="$(curl -s -X POST "$api_url/notes" -H "Content-Type: application/json" -d '{"text": "So, like, I was thinking that for the Project Phoenix meeting in Chicago, we should probably, I dont know, definitely bring the MacBook Pro. It’s just, like, totally vital for the PowerPoint sync. Honestly, at the end of the day, its just a lot of moving parts, right?"}' | jq .id -r)" # create note, capture its id

curl -X GET "$api_url/notes/$note_id" # output a note

curl -s -X GET "$api_url/notes/$note_id/phrases" | jq  '.phrases[] | [.Score, .Text] | @tsv' -r # output table of key phrases with their scores

curl -X DELETE "$api_url/notes/$note_id" # delete note

curl -X GET "$api_url/notes/$note_id" # check deleted note(should fail with 404 not found)
```
