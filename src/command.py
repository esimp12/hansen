from __future__ import annotations

from dataclasses import dataclass
from functools import partial

import typing_extensions as T


@dataclass
class Result:
    prompt: str
    params: T.Mapping[str, T.Any]
    ok: bool
    ret_val: T.Any
    err: T.Optional[Exception]
    desc: str


@dataclass
class CommandOptions:
    name: str
    action: T.Callable
    params: T.List[T.Tuple[str, T.Type]]
    prompt: str


@dataclass
class Command:
    name: str
    prompt: str
    action: T.Callable
    params: T.Mapping[str, T.Any]

    @classmethod
    def create_command(
        cls,
        name: str,
        prompt: str,
        action: T.Callable,
        param_types: T.Mapping[str, T.Type],
        param_values: T.Mapping[str, T.Any],
        history: T.List[Result],
    ) -> Command:
        params = {"history": history}

        # inject action with history
        action = partial(action, history=history)
        for param in param_types:
            if param not in param_values:
                raise ValueError(f"Missing parameter: {param}")

            param_type = param_types[param]
            param_value = param_type(param_values[param])
            params[param] = param_value
            # inject action with parameter
            action = partial(action, **{param: param_value})

        return cls(name=name, prompt=prompt, action=action, params=params)

    def execute(self) -> Result:
        try:
            ret_val, desc = self.action()
        except Exception as e:
            return Result(
                prompt=self.prompt,
                params=self.params,
                ok=False,
                ret_val=None,
                err=e,
                desc=str(e),
            )
        else:
            return Result(
                prompt=self.prompt,
                params=self.params,
                ok=True,
                ret_val=ret_val,
                err=None,
                desc=desc,
            )
