from typing import Any, Dict, Optional

from encoders import RNNEncoder_V1
from models import Model


class RNNModel_V1(Model):
    @classmethod
    def get_default_hyperparameters(cls) -> Dict[str, Any]:
        hypers = {}
        for label in ["code", "query"]:
            hypers.update({f'{label}_{key}': value
                           for key, value in RNNEncoder_V1.get_default_hyperparameters().items()})
        model_hypers = {
            'code_use_subtokens': False,
            'code_mark_subtoken_end': True,
            'batch_size': 1000
        }
        hypers.update(super().get_default_hyperparameters())
        hypers.update(model_hypers)
        return hypers

    def __init__(self,
                 hyperparameters: Dict[str, Any],
                 run_name: str = None,
                 model_save_dir: Optional[str] = None,
                 log_save_dir: Optional[str] = None):
        super().__init__(
            hyperparameters,
            code_encoder_type=RNNEncoder_V1,
            query_encoder_type=RNNEncoder_V1,
            run_name=run_name,
            model_save_dir=model_save_dir,
            log_save_dir=log_save_dir)
