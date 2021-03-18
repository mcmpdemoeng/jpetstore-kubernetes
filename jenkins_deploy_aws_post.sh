#!/bin/bash

# Get the cluster name and generate ELB name

resource_elb="eyJMb2FkQmFsYW5jZXIiOiB7ICJUeXBlIjogIkFXUzo6RWxhc3RpY0xvYWRCYWxhbmNpbmc6OkxvYWRCYWxhbmNlciIsICJEZXBlbmRzT24iOiAiVlBDR2F0ZXdheUF0dGFjaG1lbnQiLCAiRGVsZXRpb25Qb2xpY3kiOiAiRGVsZXRlIiwgIlByb3BlcnRpZXMiOiB7ICJMaXN0ZW5lcnMiOiBbIHsgIkluc3RhbmNlUG9ydCI6ICI5MDgwIiwgIkxvYWRCYWxhbmNlclBvcnQiOiAiOTA4MCIsICJQcm90b2NvbCI6ICJIVFRQIiB9IF0sICJBdmFpbGFiaWxpdHlab25lcyI6IFsgeyAiRm46OlNlbGVjdCI6IFsgIjAiLCB7ICJGbjo6R2V0QVpzIjogeyAiUmVmIjogIkFXUzo6UmVnaW9uIiB9IH0gXSB9IF0gfSB9fQ=="
resource_sg="eyJFTEJTZWN1cml0eUdyb3VwIjogeyAiRGVsZXRpb25Qb2xpY3kiOiAiRGVsZXRlIiwgIlR5cGUiOiAiQVdTOjpFQzI6OlNlY3VyaXR5R3JvdXAiLCAiUHJvcGVydGllcyI6IHsgIkdyb3VwRGVzY3JpcHRpb24iOiAiTmF0aXZlIEVMQiBzZWN1cml0eSBncm91cCIsICJWcGNJZCI6IHsgIlJlZiI6ICJWUEMiIH0sICJTZWN1cml0eUdyb3VwSW5ncmVzcyI6IFt7ICJJcFByb3RvY29sIjogInRjcCIsICJGcm9tUG9ydCI6IDgwLCAiVG9Qb3J0IjogODAsICJDaWRySXAiOiAiMC4wLjAuMC8wIiB9XSwgIlNlY3VyaXR5R3JvdXBFZ3Jlc3MiOiBbeyAiSXBQcm90b2NvbCI6ICJ0Y3AiLCAiRnJvbVBvcnQiOiA4MCwgIlRvUG9ydCI6IDgwLCAiQ2lkcklwIjogIjAuMC4wLjAvMCIgfV0gfSB9fQ=="

find_stack_name()
{
    cluster_name="petstorefortythree"
    stack_name=""
    echo "Creating new json file..."
    touch ./stacks.json
    aws cloudformation describe-stacks > ./stacks.json
    echo "Describing..."
    echo "Applying JQ..."
    stack_name=$(jq -r '."Stacks"[] | . | select(.Parameters[].ParameterValue=="'$cluster_name'") | . "StackName"'  ./stacks.json)
}

get_stack_template()
{
    echo "Creating Template file..."
    touch ./aws_stack_template.json
    echo "Pulling Template from AWS for stack: $stack_name..."
    aws cloudformation get-template --stack-name $stack_name > ./aws_stack_template.json
    ### stack_template=$(aws cloudformation get-template --stack-name $stack_name)
    echo "Done Pulling AWS Stack Template"

    ## Filtering
    echo "Filtering unwanted data from the template"
    filtered_stack_template=$(jq '."TemplateBody"' ./aws_stack_template.json)
    touch ./filtered_stack_template.json
    echo $filtered_stack_template > ./filtered_stack_template.json
    echo "Done Filtering AWS Stack Template"
}

update_template_with_resources_to_import()
{
    echo "Updating template with resources to import..."
    aws_template_version='{"AWSTemplateFormatVersion": '$(jq '."AWSTemplateFormatVersion"' ./filtered_stack_template.json)"}"
    description='{"Description": '$(jq '."Description"' ./filtered_stack_template.json)"}"
    metadata='{"Metadata": '$(jq '."Metadata"' ./filtered_stack_template.json)"}"
    parameters='{"Parameters": '$(jq '."Parameters"' ./filtered_stack_template.json)"}"
    conditions='{"Conditions": '$(jq '."Conditions"' ./filtered_stack_template.json)"}"
    resources='{"Resources": '$(jq '."Resources"' ./filtered_stack_template.json)"}"
    outputs='{"Outputs": '$(jq '."Outputs"' ./filtered_stack_template.json)"}"

    echo "separating the resource from template..."
    touch ./resources.json
    echo $resources > ./resources.json
    resource_elb_json=$(echo $resource_elb | base64 --decode)
    resource_sg_json=$(echo $resource_sg | base64 --decode)

    elb_added=$(jq ".Resources |= . + $resource_elb_json" ./resources.json)
    echo $elb_added > ./resources.json
    sg_added=$(jq ".Resources |= . + $resource_sg_json" ./resources.json)
    echo $sg_added > ./resources.json

    echo "adding the decoded resources to import to resource section..."

    echo "Merging the updated info into one template..."
    touch ./update_template.json
    echo "{}" > ./update_template.json

    aws_template_add=$(jq ". |= . + $aws_template_version" ./update_template.json)
    echo $aws_template_add > ./update_template.json

    description_add=$(jq ". |= . + $description" ./update_template.json)
    echo $description_add > ./update_template.json

    metadata_add=$(jq ". |= . + $metadata" ./update_template.json)
    echo $metadata_add > ./update_template.json

    parameters_add=$(jq ". |= . + $parameters" ./update_template.json)
    echo $parameters_add > ./update_template.json

    conditions_add=$(jq ". |= . + $conditions" ./update_template.json)
    echo $conditions_add > ./update_template.json

    updated_resources=$(jq "." ./resources.json)
    resources_add=$(jq ". |= . + $updated_resources" ./update_template.json)
    echo $resources_add > ./update_template.json

    outputs_add=$(jq ". |= . + $outputs" ./update_template.json)
    echo $outputs_add > ./update_template.json

    echo "Finished creating new template for import"
}

get_elb_and_sg_id(){
    DNS_NAME="ae19e7565469b470cb13b11a02ec94ef-1616688840.us-east-2.elb.amazonaws.com"
    elb_name=""
    sg_id=""
    echo "Creating new json file..."
    touch ./elb.json
    echo "Describing..."
    aws elb describe-load-balancers > ./elb.json
    echo "Applying JQ..."

    elb_name=$(jq -r '."LoadBalancerDescriptions"[] | . | select(.DNSName=="'$DNS_NAME'") | . "LoadBalancerName"' ./elb.json)
    sg_id=$(jq -r '."LoadBalancerDescriptions"[] | . | select(.DNSName=="'$DNS_NAME'") | . "SecurityGroups"[]' ./elb.json)
    
    echo "elb_name: $elb_name"
    echo "sg_id: $sg_id"
}

create_and_execute_change_set()
{
    echo "Creating change set"
    change_set_name=$stack_name"changeset"
    change_set_name=$elb_name"changeset"
    echo "change_set_name: $change_set_name"
    work_dir=$(pwd)
    file_location="file://$work_dir/update_template.json"
    echo "file_location: $file_location"
    aws cloudformation create-change-set --stack-name $stack_name --change-set-name $change_set_name --change-set-type IMPORT --resources-to-import "[{\"ResourceType\":\"AWS::EC2::SecurityGroup\",\"LogicalResourceId\":\"ELBSecurityGroup\",\"ResourceIdentifier\":{\"GroupId\":\"$sg_id\"}}, {\"ResourceType\":\"AWS::ElasticLoadBalancing::LoadBalancer\",\"LogicalResourceId\":\"LoadBalancer\",\"ResourceIdentifier\":{\"LoadBalancerName\":\"$elb_name\"}}]" --template-body $file_location --parameters ParameterKey="SSHKey",UsePreviousValue=true ParameterKey="Name",UsePreviousValue=true ParameterKey="ClusterRoleARN",UsePreviousValue=true ParameterKey="DBInstanceClass",UsePreviousValue=true ParameterKey="NodeRoleARN",UsePreviousValue=true ParameterKey="DBInstanceIdentifier",UsePreviousValue=true ParameterKey="MasterUserPassword",UsePreviousValue=true ParameterKey="DBEngineVersion",UsePreviousValue=true ParameterKey="MasterUsername",UsePreviousValue=true ParameterKey="DBName",UsePreviousValue=true
    aws cloudformation execute-change-set --change-set-name $change_set_name --stack-name $stack_name
}
