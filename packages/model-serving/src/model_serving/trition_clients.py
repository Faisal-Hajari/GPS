from typing import Literal
import numpy as np
import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient

INPUT_TYPES = Literal["FP32", "INT64"]
PROTOCOL = Literal["grpc", "http"]
CLIENT_MAP = {"grpc": grpcclient, "http": httpclient}


def split_inputs_into_batches(
    inputs: dict[str, np.ndarray], batch_size: int
) -> list[dict[str, np.ndarray]]:
    total_samples = next(iter(inputs.values())).shape[0]
    return [
        {name: data[i : i + batch_size] for name, data in inputs.items()}
        for i in range(0, total_samples, batch_size)
    ]


class TritonClient:
    def __init__(
        self,
        triton_url: str,
        model_name: str,
        output_names: list[str],
        protocol: PROTOCOL = "grpc",
        batch_size: int = 16,
    ) -> None:
        self.model_name = model_name
        self.output_names = output_names
        self.batch_size = batch_size
        self.lib = CLIENT_MAP[protocol]
        self.triton_url = triton_url

    @property
    def client(self):
        return self.lib.InferenceServerClient(url=self.triton_url)
    
    def _infer_batch(self, inputs: dict[str, np.ndarray], data_type: INPUT_TYPES):
        input_tensors = [
            self.lib.InferInput(name, data.shape, data_type)
            for name, data in inputs.items()
        ]
        for tensor, (_, data) in zip(input_tensors, inputs.items()):
            tensor.set_data_from_numpy(data)
        return self.client.infer(model_name=self.model_name, inputs=input_tensors)

    def inference(
        self, triton_input: dict[str, np.ndarray], input_type: INPUT_TYPES
    ) -> dict[str, np.ndarray]:
        batch_results = [
            self._infer_batch(batch, input_type)
            for batch in split_inputs_into_batches(triton_input, self.batch_size)
        ]
        return {
            output_name: np.concatenate(
                [r.as_numpy(output_name) for r in batch_results], axis=0
            )
            for output_name in self.output_names
        }