from marquetry import cuda_backend
from marquetry import Function
from marquetry import functions


class BroadcastTo(Function):
    """BroadcastTo function that transform the array to specify shape."""
    def __init__(self, shape):
        self.shape = shape

        self.x_shape = None

    def forward(self, x):
        xp = cuda_backend.get_array_module(x)
        if x.shape == self.shape:
            return x

        self.x_shape = x.shape
        y = xp.broadcast_to(x, self.shape)

        self.retain_inputs(())
        return y

    def backward(self, x, grad_y):
        if self.x_shape is None:
            return grad_y[0]

        grad_x = functions.sum_to(grad_y[0], self.x_shape)

        return grad_x


def broadcast_to(x, shape):
    """BroadcastTo function that transform the array to specify shape.

        This function copies the array to the specifying shape.

        Args:
            x (:class:`marquetry.Variable` or :class:`numpy.ndarray` or :class:`cupy.ndarray`):
                Input variable that is :class:`marquetry.Variable` array.
            shape (tuple): The goal shape using this function.

        Returns:
            marquetry.Variable: Output variable. A float array.

        Examples:

            >>> x = np.array([[1, -3]], 'f')
            >>> x
            array([[ 1., -3.]], dtype=float32)
            >>> broadcast_to(x, shape=(4, 2))
            matrix([[ 1. -3.]
                    [ 1. -3.]
                    [ 1. -3.]
                    [ 1. -3.]])

        """
    return BroadcastTo(shape)(x)
