from sparams import BaseParams


APP_NAME = "reflow_config"
class MainParams(BaseParams):
    def __init__(self, module_name):
        super().__init__(APP_NAME, module_name)
        self.endpoint_url = "/reflow_predict"
        self.response_key = "predicted_temperatures"
        self.api_port = 8002
        self.prediction_delay = 1  # giây
        self.model_dir = "models"
        self.create_or_load_yaml()
        

main_params = MainParams("main")