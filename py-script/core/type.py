from typing import Annotated, Literal, TypeVar
import numpy as np
import numpy.typing as npt

ArrayNxNx1 = Annotated[npt.NDArray[np.float32], Literal["N", "N", 1]]
