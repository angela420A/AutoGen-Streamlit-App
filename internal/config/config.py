import os
import re

import yaml
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self, config_file_path):
        self.config = None
        self.az_model_client = None

        self.load_azure_config(config_file_path)
        self.set_azure_config()

    def get_azure_model_client(self):
        return self.az_model_client

    def load_azure_config(self, config_file_path):
        with open(config_file_path, 'r') as f:
            content = f.read()

        content = re.sub(r'\$\{([^}^{]+)\}',
                         lambda m: os.environ.get(m.group(1), ""), content)
        self.config = yaml.safe_load(content)

    def set_azure_config(self):
        self.az_model_client = AzureOpenAIChatCompletionClient(
            azure_deployment=self.config.get("azure-config").get("deployment"),
            model=self.config.get("azure-config").get("model"),
            api_version=self.config.get("azure-config").get("api_version"),
            azure_endpoint=self.config.get("azure-config").get("endpoint"),
            api_key=self.config.get("azure-config").get("auth_key"),
        )
