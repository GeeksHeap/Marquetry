from marquetry import cuda_backend
from marquetry import Function
from marquetry import functions
from marquetry import utils
from marquetry.functions.connection.convolution_2d_grad_w import Conv2DGradW


class Convolution2D(Function):
    """Perform 2D convolution on an input array.

        This class defines a function that performs 2D convolution on an input array or variable using the given
        convolutional kernel and optional bias.
    """

    def __init__(self, stride=1, pad=0):
        super().__init__()
        self.stride = utils.pair(stride)
        self.pad = utils.pair(pad)

    def forward(self, x, w, b):
        xp = cuda_backend.get_array_module(x)

        kernel_height, kernel_width = w.shape[2:]
        col = utils.im2col_array(x, (kernel_height, kernel_width), self.stride, self.pad, to_matrix=False)

        y = xp.tensordot(col, w, ((1, 2, 3), (1, 2, 3)))
        if b is not None:
            y += b

        y = xp.rollaxis(y, 3, 1)

        return y

    def backward(self, inputs, grad_y):
        x, w, b = inputs
        grad_y = grad_y[0]

        grad_x = functions.deconvolution_2d(
            grad_y, w, b=None, stride=self.stride, pad=self.pad, out_size=(x.shape[2], x.shape[3]))

        grad_w = Conv2DGradW(self)(x, grad_y)

        grad_b = None

        if b is not None:
            grad_b = grad_y.sum(axis=(0, 2, 3))

        return grad_x, grad_w, grad_b


def convolution_2d(x, w, b=None, stride=1, pad=0):
    """
        Perform 2D convolution on an input array or variable.


        This class defines a function that performs 2D convolution on an input array or variable using the given
        convolutional kernel and optional bias.

        Args:
            x (:class:`marquetry.Variable` or :class:`numpy.ndarray` or :class:`cupy.ndarray`):
                The input array or variable to be convolved.
            w (:class:`marquetry.Variable` or :class:`numpy.ndarray` or :class:`cupy.ndarray`):
                The convolutional kernel.
            b (:class:`marquetry.Variable`, :class:`numpy.ndarray`, or :class:`cupy.ndarray`, optional):
                The bias term. If None, no bias is added.
            stride (int or tuple of ints, optional): The stride for moving the convolutional kernel.
                If an int is provided, it is converted to a tuple of the same value for both dimensions.
                Defaults to 1.
            pad (int or tuple of ints, optional): The padding added to the input array or variable before convolution.
                If an int is provided, it is converted to a tuple of the same value for both dimensions.
                Defaults to 0.

        Returns:
            :class:`marquetry.Variable`:
                The result of 2D convolution on the input array using the provided kernel and bias (if any).

        Examples:
            >>> x = np.arange(0, 147).reshape(1, 3, 7, 7)
            >>> w = np.ones((16, 3, 2, 2))
            >>> convolution_2d(x, w).shape
            (1, 16, 6, 6)
        """

    return Convolution2D(stride, pad)(x, w, b)
