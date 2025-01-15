from data_models.flow import Flow

class AlertManager:
    """The AlertManager class is responsible for outputting alerts generated by the SignalManager
    """

    def generate_alert(self, flow: Flow):
        print(f"[ALERT] Alert generated for flow:\n{flow}")