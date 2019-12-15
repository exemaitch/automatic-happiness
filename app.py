import os

from aws_cdk import (
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_s3,
    aws_secretsmanager,
    core,
)


class CfnPipeline(core.Stack):
    """     Creates a full pipeline with S3 storage for the build artifacts.  This code pipeline is intended to
            synth and deploy Cloud formation templates with a review and a "destination" stage.  The destination
            stage can either be your staging environment or your prod environment.

    Arguments:
        core {core.Construct} -- CDK Core construct
        id {str} -- id of the type of construct
    """

    def __init__(self, scope: core.Construct, id: str, env, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)
        bucket = aws_s3.Bucket(self, "cfn_pipeline_build_artifacts")

        # Create a source action
        source_output = aws_codepipeline.Artifact()
        source_action = aws_codepipeline_actions.GitHubSourceAction(
            action_name="Source",
            repo="automatic-happiness",
            oauth_token=core.SecretValue.secrets_manager("github_oauth_exemaitch"),
            output=source_output,
            owner="exemaitch",
        )
        gh_stage_props = aws_codepipeline.StageProps(
            stage_name="Source", actions=[source_action]
        )
        build = aws_codebuild.PipelineProject(
            self,
            "build",
            description="Runs cdk synth to output Cloudformation template",
            environment=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2,
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                "./buildspecs/s3_to_cdk.yml"
            ),
        )

        cfn_pipeline = aws_codepipeline.Pipeline(
            self,
            "CFN Pipeline",
            artifact_bucket=bucket,
            stages=[
                gh_stage_props,
                aws_codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name="FoobarBuild",
                            project=build,
                            input=source_output,
                        )
                    ],
                ),
            ],
        )


app = core.App()
CfnPipeline(
    app,
    "CfnPipeline",
    env=core.Environment(
        account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
        region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
    ),
)
app.synth()
