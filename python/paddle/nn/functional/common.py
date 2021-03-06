#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings
import paddle
from ...fluid.framework import in_dygraph_mode, default_main_program
from paddle.fluid.layer_helper import LayerHelper
from paddle.fluid.layers.tensor import Variable, fill_constant, zeros, concat

# TODO: define the common functions to build a neural network  
from ...fluid.layers import label_smooth  #DEFINE_ALIAS
from ...fluid import one_hot  #DEFINE_ALIAS
from ...fluid.layers import pad2d  #DEFINE_ALIAS
from ...fluid.layers import unfold  #DEFINE_ALIAS
from ...fluid.layers import assign  #DEFINE_ALIAS
from ...fluid.layers import squeeze  #DEFINE_ALIAS
from ...fluid.layers import unsqueeze  #DEFINE_ALIAS
from ...fluid.layers import elementwise_mul  #DEFINE_ALIAS
from ...tensor import clip
from ...tensor import sum
from ...tensor import sqrt

#from ...fluid.layers import fc  #DEFINE_ALIAS
from ...fluid.layers import pad_constant_like  #DEFINE_ALIAS
from ...fluid import core, layers
from ...fluid.data_feeder import check_variable_and_dtype

__all__ = [
    'dropout',
    'dropout2d',
    'dropout3d',
    #       'embedding',
    #       'fc',
    'label_smooth',
    'one_hot',
    'pad',
    'pad_constant_like',
    'pad2d',
    'unfold',
    #       'bilinear_tensor_product',
    'assign',
    'interpolate',
    'cosine_similarity',
]


def interpolate(input,
                size=None,
                scale_factor=None,
                mode='nearest',
                align_corners=False,
                align_mode=1,
                data_format='NCHW',
                name=None):
    """
	:alias_main: paddle.nn.functional.interpolate
	:alias: paddle.nn.functional.interpolate,paddle.nn.functional.common.interpolate

    This op resizes a batch of images.
    The input must be a 3-D Tensor of the shape (num_batches, channels, in_w)
    or 4-D (num_batches, channels, in_h, in_w), or a 5-D Tensor of the shape
    (num_batches, channels, in_d, in_h, in_w) or (num_batches, in_d, in_h, in_w, channels),
    and the resizing only applies on the three dimensions(depth, height and width).
    **Warning:** the parameter :attr:`actual_shape` will be deprecated in the
    future and only use :attr:`out_shape` instead.
    Supporting resample methods:
        'linear' : Linear interpolation
        'bilinear' : Bilinear interpolation
        'trilinear' : Trilinear interpolation
        'nearest' : Nearest neighbor interpolation
        'bicubic' : Bicubic interpolation

    Linear interpolation is the method of using a line connecting two known quantities 
    to determine the value of an unknown quantity between the two known quantities. 
    
    Nearest neighbor interpolation is to perform nearest neighbor interpolation
    in both the 3rd dimension(in height direction) and the 4th dimension(in width
    direction) on input tensor.

    Bilinear interpolation is an extension of linear interpolation for
    interpolating functions of two variables (e.g. H-direction and
    W-direction in this op) on a rectilinear 2D grid. The key idea is
    to perform linear interpolation first in one direction, and then
    again in the other direction.

    Trilinear interpolation is an extension of linear interpolation for
    interpolating functions of three variables (e.g. D-direction,
    H-direction and W-direction in this op) on a rectilinear 3D grid.
    The linear interpolation is performed on three directions.
    Align_corners and align_mode are optional parameters,the calculation method
    of interpolation can be selected by them.

    Bicubic interpolation is an extension of cubic interpolation for interpolating
    data points on a two-dimensional regular grid. The interpolated surface is
    smoother than corresponding surfaces obtained by bilinear interpolation or
    nearest-neighbor interpolation.

    Example:

    .. code-block:: text

        For scale_factor:
            if align_corners = True && out_size > 1 :
              scale_factor = (in_size-1.0)/(out_size-1.0)
            else:
              scale_factor = float(in_size/out_size)

        Linear interpolation:
            if:
                align_corners = False , align_mode = 0
                input : (N,C,W_in)
                output: (N,C,W_out) where:
                W_out = (W_{in}+0.5) * scale_{factor} - 0.5
            else:
                input : (N,C,W_in)
                output: (N,C,W_out) where:
                W_out = W_{in} * scale_{factor}
        
        Nearest neighbor interpolation:
          if:
              align_corners = False
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = floor (H_{in} * scale_{factor})
              W_out = floor (W_{in} * scale_{factor})
          else:
              align_corners = True
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = round(H_{in} * scale_{factor})
              W_out = round(W_{in} * scale_{factor})

        Bilinear interpolation:
          if:
              align_corners = False , align_mode = 0
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = (H_{in}+0.5) * scale_{factor} - 0.5
              W_out = (W_{in}+0.5) * scale_{factor} - 0.5
          else:
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = H_{in} * scale_{factor}
              W_out = W_{in} * scale_{factor}

        Bicubic interpolation:
          if:
              align_corners = False
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = (H_{in}+0.5) * scale_{factor} - 0.5
              W_out = (W_{in}+0.5) * scale_{factor} - 0.5
          else:
              input : (N,C,H_in,W_in)
              output: (N,C,H_out,W_out) where:
              H_out = H_{in} * scale_{factor}
              W_out = W_{in} * scale_{factor}

        Trilinear interpolation:
          if:
              align_corners = False , align_mode = 0
              input : (N,C,D_in,H_in,W_in)
              output: (N,C,D_out,H_out,W_out) where:
              D_out = (D_{in}+0.5) * scale_{factor} - 0.5
              H_out = (H_{in}+0.5) * scale_{factor} - 0.5
              W_out = (W_{in}+0.5) * scale_{factor} - 0.5
          else:
              input : (N,C,D_in,H_in,W_in)
              output: (N,C,D_out,H_out,W_out) where:
              D_out = D_{in} * scale_{factor}
              H_out = H_{in} * scale_{factor}
              W_out = W_{in} * scale_{factor}

    For details of linear interpolation, please refer to Wikipedia:
    https://en.wikipedia.org/wiki/Linear_interpolation.
    
    For details of nearest neighbor interpolation, please refer to Wikipedia:
    https://en.wikipedia.org/wiki/Nearest-neighbor_interpolation.
    
    For details of bilinear interpolation, please refer to Wikipedia:
    https://en.wikipedia.org/wiki/Bilinear_interpolation.
    
    For details of trilinear interpolation, please refer to Wikipedia:
    https://en.wikipedia.org/wiki/Trilinear_interpolation.
    
    For details of bicubic interpolation, please refer to Wikipedia:
    https://en.wikipedia.org/wiki/Bicubic_interpolation
    
    Parameters:
        input (Variable): 3-D, 4-D or 5-D Tensor, its data type is float32, float64, or uint8,
                          its data format is specified by :attr:`data_format`.
        size (list|tuple|Variable|None): Output shape of image resize
             layer, the shape is (out_w, ) when input is a 3-D Tensor, the shape is (out_h, out_w) 
             when input is a 4-D Tensor and is (out_d, out_h, out_w) when input is a 5-D Tensor. 
             Default: None. If a list, each element can be an integer or a Tensor Variable of shape: [1].
             If a Tensor Variable, its dimensions size should be a 1.
        scale_factor (float|Variable|None): The multiplier for the input height or width. At
             least one of :attr:`out_shape` or :attr:`scale_factor` must be set.
             And :attr:`out_shape` has a higher priority than :attr:`scale_factor`.
             Default: None.
        mode (str): The resample method. It supports 'linear', 'nearest', 'bilinear',
                       'bicubic' and 'trilinear' currently. Default: 'nearest'
        align_corners(bool) :  An optional bool, If True, the centers of the 4 corner pixels of the
                               input and output tensors are aligned, preserving the values at the
                               corner pixels.
                               Default: False
        align_mode(int)  :  An optional for linear/bilinear/trilinear interpolation. Refer to the formula in the example above,
                            it can be \'0\' for src_idx = scale_factor*(dst_indx+0.5)-0.5 , can be \'1\' for
                            src_idx = scale_factor*dst_index.
        data_format (str, optional): Specify the data format of the input, and the data format of the output
            will be consistent with that of the input. An optional string from:`NCW`, `NWC`,  `"NCHW"`, `"NHWC"`, `"NCDHW"`,
            `"NDHWC"`. The default is `"NCHW"`. When it is `"NCHW"`, the data is stored in the order of:
            `[batch_size, input_channels, input_height, input_width]`. When it is `"NCHW"`, the data is stored
            in the order of: `[batch_size, input_channels, input_depth, input_height, input_width]`.
        name(str, optional): The default value is None.
                             Normally there is no need for user to set this property.
                             For more information, please refer to :ref:`api_guide_Name`
    Returns:
        A 3-D Tensor of the shape (num_batches, channels, out_w) or (num_batches, out_w, channels),
        A 4-D Tensor of the shape (num_batches, channels, out_h, out_w) or (num_batches, out_h, out_w, channels),
        or 5-D Tensor of the shape (num_batches, channels, out_d, out_h, out_w) or (num_batches, out_d, out_h, out_w, channels).
    Raises:
        TypeError: size should be a list or tuple or Variable.
        ValueError: The 'mode' of image_resize can only be 'linear', 'bilinear',
                    'trilinear', 'bicubic', or 'nearest' currently.
        ValueError: 'linear' only support 3-D tensor.
        ValueError: 'bilinear', 'bicubic' and 'nearest' only support 4-D tensor.
        ValueError: 'trilinear' only support 5-D tensor.
        ValueError: One of size and scale_factor must not be None.
        ValueError: size length should be 1 for input 3-D tensor.
        ValueError: size length should be 2 for input 4-D tensor.
        ValueError: size length should be 3 for input 5-D tensor.
        ValueError: scale_factor should be greater than zero.
        TypeError: align_corners should be a bool value
        ValueError: align_mode can only be '0' or '1'
        ValueError: data_format can only be 'NCW', 'NWC', 'NCHW', 'NHWC', 'NCDHW' or 'NDHWC'.

    Examples:
        .. code-block:: python

	    #declarative mode
	    import paddle
	    import numpy as np
	    input = fluid.data(name="input", shape=[None,3,6,10])
	    #1
	    output = paddle.nn.functional.interpolate(input=input, size=[12,12])
	    #2
	    #x = np.array([2]).astype("int32")
	    #dim1 = fluid.data(name="dim1", shape=[1], dtype="int32")
	    #fluid.layers.assign(input=x, output=dim1)
	    #output = paddle.nn.functional.interpolate(input=input, size=[12,dim1])
	    #3
	    #x = np.array([3,12]).astype("int32")
	    #shape_tensor = fluid.data(name="shape_tensor", shape=[2], dtype="int32")
	    #fluid.layers.assign(input=x, output=shape_tensor)
	    #output = paddle.nn.functional.interpolate(input=input, size=shape_tensor)
	    #4
	    #x = np.array([0.5]).astype("float32")
	    #scale_tensor = fluid.data(name="scale", shape=[1], dtype="float32")
	    #fluid.layers.assign(x,scale_tensor)
	    #output = paddle.nn.functional.interpolate(input=input, scale_factor=scale_tensor)
	    place = fluid.CPUPlace()
	    exe = fluid.Executor(place)
	    exe.run(fluid.default_startup_program())

	    input_data = np.random.rand(2,3,6,10).astype("float32")
	    output_data = exe.run(fluid.default_main_program(),
                feed={"input":input_data},
                fetch_list=[output],
                return_numpy=True)

	    print(output_data[0].shape)
	    #1
	    # (2, 3, 12, 12)
	    #2
	    # (2, 3, 12, 2)
	    #3
	    # (2, 3, 3, 12)
	    #4
	    # (2, 3, 3, 5)
	    #imperative mode
	    import paddle.fluid.dygraph as dg
	    with dg.guard(place) as g:
    		input = dg.to_variable(input_data)
    		output = paddle.nn.functional.interpolate(input=input, size=[12,12])
    		print(output.shape)
		# [2L, 3L, 12L, 12L]
    """
    data_format = data_format.upper()
    resample = mode.upper()
    resample_type = mode.lower()

    resample_methods = [
        'LINEAR',
        'BILINEAR',
        'TRILINEAR',
        'NEAREST',
        'BICUBIC',
    ]
    if resample not in resample_methods:
        raise ValueError(
            "The 'resample' of image_resize can only be 'linaer', 'bilinear', 'trilinear', "
            " 'bicubic' or 'nearest' currently.")

    if resample in ['LINEAR'] and len(input.shape) != 3:
        raise ValueError("'linear' only support 3-D tensor.")

    if resample in ['BILINEAR', 'NEAREST', 'BICUBIC'] and len(input.shape) != 4:
        raise ValueError(
            "'bilinear', 'bicubic' and 'nearest' only support 4-D tensor.")
    if resample == 'TRILINEAR' and len(input.shape) != 5:
        raise ValueError("'trilinear'only support 5-D tensor.")

    if size is None and scale_factor is None:
        raise ValueError("One of size and scale_factor must not be None.")

    if not isinstance(align_corners, bool):
        raise TypeError("Attr align_corners should be a bool value")

    if align_mode != 0 and align_mode != 1:
        raise ValueError("align_mode can only be 0 or 1")

    helper = LayerHelper('{}_interp'.format(resample_type), **locals())
    dtype = helper.input_dtype()

    if len(input.shape) == 3 and data_format not in ['NCW', 'NWC']:
        raise ValueError(
            "Got wrong value for param `data_format`: " + data_format +
            " received but only `NCW` or `NWC` supported for 3-D input.")
    elif len(input.shape) == 4 and data_format not in ['NCHW', 'NHWC']:
        raise ValueError(
            "Got wrong value for param `data_format`: " + data_format +
            " received but only `NCHW` or `NHWC` supported for 4-D input.")
    elif len(input.shape) == 5 and data_format not in ['NCDHW', 'NDHWC']:
        raise ValueError(
            "Got wrong value for param `data_format`: " + data_format +
            " received but only `NCDHW` or `NDHWC` supported for 5-D input.")

    def _is_list_or_turple_(data):
        return (isinstance(data, list) or isinstance(data, tuple))

    if data_format == 'NCHW' or data_format == 'NCDHW' or data_format == 'NCW':
        data_layout = 'NCHW'
    if data_format == 'NHWC' or data_format == 'NDHWC' or data_format == 'NWC':
        data_layout = 'NHWC'

    inputs = {"X": input}
    attrs = {
        "out_d": -1,
        "out_h": -1,
        "out_w": -1,
        "interp_method": resample_type,
        "align_corners": align_corners,
        "align_mode": align_mode,
        "data_layout": data_layout
    }

    out_shape = size
    scale = scale_factor
    if out_shape is not None:
        if isinstance(out_shape, Variable):
            out_shape.stop_gradient = True
            inputs['OutSize'] = out_shape
        else:
            if not (_is_list_or_turple_(out_shape)):
                raise TypeError(
                    "out_shape should be a list or tuple or Variable.")
            # Validate the shape
            contain_var = False
            for dim_idx, dim_size in enumerate(out_shape):
                if isinstance(dim_size, Variable):
                    contain_var = True
                    continue
                assert dim_size > 0, (
                    "Each dimension size given in out_shape must be greater than 0."
                )

            if contain_var:
                new_size_tensor = []
                size_list = []
                for dim in out_shape:
                    if isinstance(dim, Variable):
                        dim.stop_gradient = True
                        new_size_tensor.append(dim)
                        size_list.append(-1)
                    else:
                        assert (isinstance(dim, int))
                        temp_out = helper.create_variable_for_type_inference(
                            'int32')
                        fill_constant(
                            [1], 'int32', dim, force_cpu=True, out=temp_out)
                        new_size_tensor.append(temp_out)
                        size_list.append(dim)
                inputs['SizeTensor'] = new_size_tensor

            if len(input.shape) == 3:
                if len(out_shape) != 1:
                    raise ValueError(
                        "out_shape length should be 2 for input 3-D tensor")
                if contain_var:
                    attrs['out_w'] = size_list[0]
                else:
                    out_shape = list(map(int, out_shape))
                    attrs['out_w'] = out_shape[0]
            if len(input.shape) == 4:
                if len(out_shape) != 2:
                    raise ValueError("out_shape length should be 2 for "
                                     "input 4-D tensor.")
                if contain_var:
                    attrs['out_h'] = size_list[0]
                    attrs['out_w'] = size_list[1]
                else:
                    out_shape = list(map(int, out_shape))
                    attrs['out_h'] = out_shape[0]
                    attrs['out_w'] = out_shape[1]
            if len(input.shape) == 5:
                if len(out_shape) != 3:
                    raise ValueError("out_shape length should be 3 for "
                                     "input 5-D tensor.")
                if contain_var:
                    attrs['out_d'] = size_list[0]
                    attrs['out_h'] = size_list[1]
                    attrs['out_w'] = size_list[2]
                else:
                    out_shape = list(map(int, out_shape))
                    attrs['out_d'] = out_shape[0]
                    attrs['out_h'] = out_shape[1]
                    attrs['out_w'] = out_shape[2]

    else:
        if isinstance(scale, Variable):
            scale.stop_gradient = True
            inputs["Scale"] = scale
        elif isinstance(scale, float) or isinstance(scale, int):
            if scale <= 0:
                raise ValueError("Attr(scale) should be greater than zero.")
            attrs['scale'] = float(scale)
        else:
            raise TypeError(
                "Attr(scale)'s type should be float, int or Variable.")

    out = helper.create_variable_for_type_inference(dtype)
    helper.append_op(
        type='{}_interp'.format(resample_type),
        inputs=inputs,
        outputs={"Out": out},
        attrs=attrs)
    return out


def dropout(x,
            p=0.5,
            axis=None,
            training=True,
            mode="upscale_in_train",
            name=None):
    """
    Dropout is a regularization technique for reducing overfitting by preventing
    neuron co-adaption during training. The dropout operator randomly sets the
    outputs of some units to zero, while upscale others according to the given
    dropout probability.

    Args:
        x (Tensor): The input tensor. The data type is float32 or float64.
        p (float | int): Probability of setting units to zero. Default 0.5.
        axis (int | list): The axis along which the dropout is performed. Default None.
        training (bool): A flag indicating whether it is in train phrase or not. Default True.
        name (str, optional): Name for the operation (optional, default is None). For more information, please refer to :ref:`api_guide_Name`.
        mode(str): ['upscale_in_train'(default) | 'downscale_in_infer']

                           1. upscale_in_train(default), upscale the output at training time

                              - train: out = input * mask / ( 1.0 - dropout_prob )
                              - inference: out = input

                           2. downscale_in_infer, downscale the output at inference

                              - train: out = input * mask
                              - inference: out = input * (1.0 - dropout_prob)

    Returns:
        A Tensor representing the dropout, has same shape and data type as `x` .

    Examples:
        We use ``p=0.5`` in the following description for simplicity.
        1. When ``axis=None`` , this is commonly used dropout, which dropout each element of x randomly.
            Let's see a simple case when x is a 2d tensor with shape 2*3:
            [[1 2 3]
             [4 5 6]]
            we generate mask with the same shape as x, which is 2*3. The value of mask is
            sampled from a Bernoulli distribution randomly. For example, we may get such mask:
            [[0 1 0]
             [1 0 1]]
            So the output is obtained from elementwise multiply of x and mask:
            [[0 2 0]
             [4 0 6]]
            Using default setting, i.e. ``mode='upscale_in_train'`` ,
            if in training phase, the final upscale output is:
            [[0 4 0 ]
             [8 0 12]]
            if in test phase, the output is the same as input:
            [[1 2 3]
             [4 5 6]]
            we can also set ``mode='downscale_in_infer'`` , then
            if in training phase, the final output is:
            [[0 2 0]
             [4 0 6]]
            if in test phase, the scale output is:
            [[0.5 1.  1.5]
             [2.  2.5 3. ]]

        2. When ``axis!=None`` , this is useful for dropping whole channels from an image or sequence.
            Let's see the simple case when x is a 2d tensor with shape 2*3 again:
            [[1 2 3]
             [4 5 6]]
            (1) If ``axis=0`` , this means the dropout is only performed in axis `0` .
                we generate mask with the shape 2*1. Only in axis `0` the value is randomly selected.
                For example, we may get such mask:
                [[1]
                 [0]]
                The output is obtained from elementwise multiply of x and mask. Doing that the mask will be
                broadcast from 2*1 to 2*3:
                [[1 1 1]
                 [0 0 0]]
                and the result after elementwise multiply is:
                [[1 2 3]
                 [0 0 0]]
                then we can do upscale or downscale according to the setting of other arguments.
            (2) If ``axis=1`` , this means the dropout is only performed in axis `1` .
                we generate mask with the shape 1*3. Only in axis `1` the value is randomly selected.
                For example, we may get such mask:
                [[1 0 1]]
                Doing elementwise multiply the mask will be broadcast from 1*3 to 2*3:
                [[1 0 1]
                 [1 0 1]]
                and the result after elementwise multiply is:
                [[1 0 3]
                 [4 0 6]]
            (3) What about ``axis=[0, 1]`` ? This means the dropout is performed in all axes of x,
                which is the same case as default setting ``axis=None`` .
            (4) You may note that logically `axis=None` means the dropout is performed in no axis of x,
                We generate mask with the shape 1*1. Whole input is randomly selected or dropped.
                For example, we may get such mask:
                [[0]]
                Doing elementwise multiply the mask will be broadcast from 1*1 to 2*3:
                [[0 0 0]
                 [0 0 0]]
                and the result after elementwise multiply is:
                [[0 0 0]
                 [0 0 0]]
                Actually this is not what we want because all elements may set to zero~
            When x is a 4d tensor with shape `NCHW`, we can set ``axis=[0,1]`` and the dropout will be performed
            in channel `N` and `C`, `H` and `W` is tied, i.e.
            paddle.nn.dropout(x, p, axis=[0,1])
            This is something we called dropout2d. Please refer to ``paddle.nn.functional.dropout2d``
            for more details.
            Similarly, when x is a 5d tensor with shape `NCDHW`, we can set ``axis=[0,1]`` to perform
            dropout3d. Please refer to ``paddle.nn.functional.dropout3d`` for more details.

        .. code-block:: python
            import paddle
            import numpy as np

            paddle.disable_static()
            x = np.array([[1,2,3], [4,5,6]]).astype('float32')
            x = paddle.to_tensor(x)
            y_train = paddle.nn.functional.dropout(x, 0.5)
            y_test = paddle.nn.functional.dropout(x, 0.5, training=False) 
            y_0 = paddle.nn.functional.dropout(x, axis=0)
            y_1 = paddle.nn.functional.dropout(x, axis=1)
            y_01 = paddle.nn.functional.dropout(x, axis=[0,1])
            print(x.numpy())
            print(y_train.numpy())
            print(y_test.numpy())
            print(y_0.numpy())
            print(y_1.numpy())
            print(y_01.numpy())

    """
    if not isinstance(p, (float, int)):
        raise TypeError("p argument should be a number")
    if p < 0 or p > 1:
        raise ValueError("p argument should between 0 and 1")
    if mode not in ('downscale_in_infer', 'upscale_in_train'):
        raise ValueError(
            "mode argument should be 'downscale_in_infer' or 'upscale_in_train'")
    if axis and not isinstance(axis, (int, list)):
        raise TypeError("datatype of axis argument should be int or list")

    if axis == None:  # commonly used dropout
        seed = None
        mode = 'downgrade_in_infer' if mode == 'downscale_in_infer' else mode  #semantic transfer

        def get_attrs(prog, dropout_prob, is_test, seed):
            if (seed is None or seed == 0) and prog.random_seed != 0:
                seed = prog.random_seed
            attrs = {
                'dropout_prob': dropout_prob,
                'is_test': is_test,
                'fix_seed': seed is not None,
                'seed': seed if seed is not None else 0,
                'dropout_implementation': mode,
            }
            return attrs

        if in_dygraph_mode():
            if default_main_program().random_seed != 0:
                seed = default_main_program().random_seed
            out, mask = core.ops.dropout(
                x, 'dropout_prob', p, 'is_test', not training, 'fix_seed',
                seed is not None, 'seed', seed
                if seed is not None else 0, 'dropout_implementation', mode)
            return out

        helper = LayerHelper('dropout', **locals())
        check_variable_and_dtype(x, 'x', ['float16', 'float32', 'float64'],
                                 'dropout')

        out = helper.create_variable_for_type_inference(dtype=x.dtype)
        mask = helper.create_variable_for_type_inference(
            dtype=core.VarDesc.VarType.UINT8, stop_gradient=True)

        attrs = get_attrs(helper.main_program, p, not training, seed)

        helper.append_op(
            type='dropout',
            inputs={'X': [x]},
            outputs={'Out': [out],
                     'Mask': [mask]},
            attrs=attrs)
        return out
    else:  #sometimes called dropout_nd #TODO: optimize with c++
        if not in_dygraph_mode():
            check_variable_and_dtype(x, 'x', ['float32', 'float64'], 'dropout')
        dtype = x.dtype
        keep_prob = 1 - p
        if training:
            if p == 1.:
                return layers.scale(x, scale=0.)

            scale_input = layers.scale(
                x, scale=1 / keep_prob) if mode == 'upscale_in_train' else x

            #get mask shape
            input_shape = x.shape
            drop_axes = [axis] if isinstance(axis, int) else axis
            if max(drop_axes) > len(input_shape) - 1:
                raise ValueError("axis value should less than dimensions of x:{}, but get drop_axes value:{} " \
                                 .format(len(input_shape), max(drop_axes)))
            if len(drop_axes) > len(input_shape):
                raise ValueError(
                    "length of axis should not greater than dimensions of x:{}, but get length of drop axes: {}".
                    format(len(input_shape), len(drop_axes)))
            mask_shape = [1] * len(input_shape)
            for i in drop_axes:
                mask_shape[i] = input_shape[i]

            #get mask
            random_tensor = layers.uniform_random(
                mask_shape, dtype='float32', min=0., max=1.0)
            p = layers.fill_constant(shape=[1], dtype='float32', value=p)
            keep_mask = layers.greater_equal(random_tensor, p)

            scale_input = layers.cast(scale_input, dtype)
            keep_mask = layers.cast(keep_mask, dtype)
            ret = paddle.multiply(scale_input, keep_mask, name=name)
            return ret
        else:  # test
            ret = layers.scale(
                x, scale=keep_prob) if mode == 'downscale_in_infer' else x
            return ret


def dropout2d(x, p=0.5, training=True, data_format='NCHW', name=None):
    """
    Randomly zero out entire channels (in the batched input 4d tensor with the shape `NCHW` ,
    a channel is a 2D feature map with the shape `HW` ). Each channel will be zeroed out independently
    on every forward call with probability `p` using samples from a Bernoulli distribution.

    See ``paddle.nn.functional.dropout`` for more details.

    Args:
        x (Tensor):  The input is 4-D Tensor with shape [N, C, H, W] or [N, H, W, C].
                     The data type is float32 or float64.
        p (float): Probability of setting units to zero. Default 0.5.
        training (bool): A flag indicating whether it is in train phrase or not. Default True.
        data_format (str, optional): Specify the data format of the input, and the data format of the output
                                     will be consistent with that of the input. An optional string from:
                                    `NCHW` , `NHWC` . The default is `NCHW` . When it is `NCHW` , the data is
                                    stored in the order of: [batch_size, input_channels, input_height, input_width].
        name (str, optional): Name for the operation (optional, default is None). For more information, please refer to :ref:`api_guide_Name`.

    Returns:
        A Tensor representing the dropout2d, has same shape and data type as `x` .

    Examples:
        .. code-block:: python
            import paddle
            import numpy as np

            paddle.disable_static()
            x = np.random.random(size=(2, 3, 4, 5)).astype('float32')
            x = paddle.to_tensor(x)
            y_train = paddle.nn.functional.dropout2d(x)  #train
            y_test = paddle.nn.functional.dropout2d(x, training=False) #test
            for i in range(2):
                for j in range(3):
                    print(x.numpy()[i,j,:,:])
                    print(y_train.numpy()[i,j,:,:]) # may all 0
                    print(y_test.numpy()[i,j,:,:])
    """
    input_shape = x.shape
    if len(input_shape) != 4:
        raise ValueError("dimensions of x should be 4, but received {} != 4"\
        .format(len(input_shape)))

    if data_format not in ["NCHW", "NHWC"]:
        raise ValueError(
            "Attr(data_format) should be 'NCHW' or 'NHWC'. Received "
            "Attr(data_format): %s." % str(data_format))

    return dropout(
        x,
        p=p,
        axis=[0, 1] if data_format == 'NCHW' else [0, 3],
        training=training,
        mode="upscale_in_train",
        name=name)


def dropout3d(x, p=0.5, training=True, data_format='NCDHW', name=None):
    """
    Randomly zero out entire channels (in the batched input 5d tensor with the shape `NCDHW` ,
    a channel is a 3D feature map with the shape `DHW` ). Each channel will be zeroed out independently
    on every forward call with probability `p` using samples from a Bernoulli distribution.

    See ``paddle.nn.functional.dropout`` for more details.

    Args:
        x (Tensor):  The input is 5-D Tensor with shape [N, C, D, H, W] or [N, D, H, W, C].
                     The data type is float32 or float64.
        p (float): Probability of setting units to zero. Default 0.5.
        training (bool): A flag indicating whether it is in train phrase or not. Default True.
        data_format (str, optional): Specify the data format of the input, and the data format of the output
                                     will be consistent with that of the input. An optional string from:
                                    ``NCDHW``, ``NDHWC``. The default is ``NCDHW`` . When it is ``NCDHW`` , the data is
                                    stored in the order of: [batch_size, input_channels, input_depth, input_height, input_width].
        name (str, optional): Name for the operation (optional, default is None). For more information, please refer to :ref:`api_guide_Name`.

    Returns:
        A Tensor representing the dropout3d, has same shape and data type with `x` .

    Examples:
        .. code-block:: python
            import paddle
            import numpy as np

            paddle.disable_static()
            x = np.random.random(size=(2, 3, 4, 5, 6)).astype('float32')
            x = paddle.to_tensor(x)
            y_train = paddle.nn.functional.dropout3d(x)  #train
            y_test = paddle.nn.functional.dropout3d(x, training=False) #test
            print(x.numpy()[0,0,:,:,:])
            print(y_train.numpy()[0,0,:,:,:]) # may all 0
            print(y_test.numpy()[0,0,:,:,:])
    """

    input_shape = x.shape
    if len(input_shape) != 5:
        raise ValueError("dimensions of x should be 5, but received {} != 5" \
        .format(len(input_shape)))

    if data_format not in ["NCDHW", "NDHWC"]:
        raise ValueError(
            "Attr(data_format) should be 'NCDHW' or 'NDHWC'. Received "
            "Attr(data_format): %s." % str(data_format))

    return dropout(
        x,
        p=p,
        axis=[0, 1] if data_format == 'NCDHW' else [0, 4],
        training=training,
        mode="upscale_in_train",
        name=name)


def pad(x, pad, mode='constant', value=0, data_format="NCHW", name=None):
    """
    Pad tensor according to 'pad' and 'mode'.
    If mode is 'reflect', pad[0] and pad[1] must be no greater
    than width-1. The height and depth dimension has the same condition.

    Parameters:
        x (Tensor): The input tensor with data type float32/double/int32/int64_t.
        pad (Tensor | List[int32]): The padding size with data type int32. [len(padding)/2] dimensions
            of input will be padded. 1. If input dimension is 3, then the pad has the form (pad_left,
            pad_right). 2. If the input dimension is 4, then the pad has the form (pad_left, pad_right, 
            pad_top, pad_bottom). 3. If the input dimension is 5, then the pad has the form 
            (pad_left, pad_right, pad_top, pad_bottom, pad_front, pad_back).
            
        mode (str): Four modes: 'constant' (default), 'reflect', 'replicate', 'circular'.
            When in 'constant' mode, this op uses a constant value to pad the input tensor.
            When in 'reflect' mode, uses reflection of the input boundaries to pad the input tensor.
            When in 'replicate' mode, uses input boundaries to pad the input tensor.
            When in 'circular' mode, uses circular input to pad the input tensor.
            Default is 'constant'
        value (float32): The value to fill the padded areas in 'constant' mode . Default is 0.0
        data_format (str): An string from: "NCL", "NLC", NHWC", "NCHW", "NCDHW", "NDHWC". Specify the data format of
           the input data.
           Default is  "NCHW"
        name (str, optional) : The default value is None.  Normally there is no need for
            user to set this property.  For more information, please refer to :ref:`api_guide_Name`.
                    
    Returns: a Tensor padded according to pad and mode and data type is same as input.
    Return Type: Tensor

    Examples:
        .. code-block:: text

            x = [[[[[1., 2., 3.],
                    [4., 5., 6.]]]]]

            Case 0:
                pad = [2, 2, 1, 1, 0, 0],
                mode = 'constant'
                value = 0
                Out = [[[[[0. 0. 0. 0. 0. 0. 0.]
                          [0. 0. 1. 2. 3. 0. 0.]
                          [0. 0. 4. 5. 6. 0. 0.]
                          [0. 0. 0. 0. 0. 0. 0.]]]]]

            Case 1:
                pad = [2, 2, 1, 1, 0, 0],
                mode = 'reflect'
                Out = [[[[[6. 5. 4. 5. 6. 5. 4.]
                          [3. 2. 1. 2. 3. 2. 1.]
                          [6. 5. 4. 5. 6. 5. 4.]
                          [3. 2. 1. 2. 3. 2. 1.]]]]]

            Case 2:
                pad = [2, 2, 1, 1, 0, 0],
                mode = 'replicate'
                Out = [[[[[1. 1. 1. 2. 3. 3. 3.]
                          [1. 1. 1. 2. 3. 3. 3.]
                          [4. 4. 4. 5. 6. 6. 6.]
                          [4. 4. 4. 5. 6. 6. 6.]]]]]

            Case 3:
                pad = [2, 2, 1, 1, 0, 0],
                mode = 'circular'
                Out = [[[[[5. 6. 4. 5. 6. 4. 5.]
                          [2. 3. 1. 2. 3. 1. 2.]
                          [5. 6. 4. 5. 6. 4. 5.]
                          [2. 3. 1. 2. 3. 1. 2.]]]]]

    Code Examples:
        .. code-block:: python
            import numpy as np
            import paddle
            import paddle.nn.functional as F
            
            paddle.disable_static()
            
            # example 1
            x_shape = (1, 1, 3)
            x = np.arange(np.prod(x_shape), dtype=np.float32).reshape(x_shape) + 1
            tensor_x = paddle.to_tensor(x)
            y = F.pad(tensor_x, pad=[2, 3], value=1, mode='constant')
            print(y.numpy())
            # [[[1. 1. 1. 2. 3. 1. 1. 1.]]]
            
            # example 2
            x_shape = (1, 1, 2, 3)
            x = np.arange(np.prod(x_shape), dtype=np.float32).reshape(x_shape) + 1
            tensor_x = paddle.to_tensor(x)
            y = F.pad(tensor_x, pad=[1, 2, 1, 1], value=1, mode='circular')
            print(y.numpy())
            # [[[[6. 4. 5. 6. 4. 5.]
            #    [3. 1. 2. 3. 1. 2.]
            #    [6. 4. 5. 6. 4. 5.]
            #    [3. 1. 2. 3. 1. 2.]]]]
    """
    assert mode in ['reflect', 'replicate', 'constant', 'circular'], \
            "mode should be one of constant, reflect, replicate, circular, but got {}.".format(mode)

    data_format = data_format.upper()
    assert data_format in ["NCL", "NCHW", "NCDHW", "NLC", "NHWC", "NDHWC"], \
        "data_format should be in one of [NCL, NCHW, NCDHW, NLC, NHWC, NDHWC], " \
        "but got {}".format(data_format)

    x_dim = len(x.shape)

    original_data_format = data_format
    unsqueezed_dim = []

    if isinstance(pad, Variable):
        if data_format in ["NCL", "NCHW", "NCDHW"]:
            data_format = "NCDHW"
            if x_dim == 3:
                pad = concat([zeros((4, ), dtype="int32"), pad], axis=0)
                unsqueezed_dim = [3, 4]
                x = unsqueeze(x, axes=unsqueezed_dim)
            elif x_dim == 4:
                pad = concat([pad, zeros((2, ), dtype="int32")], axis=0)
                unsqueezed_dim = [2]
                x = unsqueeze(x, axes=unsqueezed_dim)
        elif data_format in ["NLC", "NHWC", "NDHWC"]:
            data_format = "NDHWC"
            if x_dim == 3:
                pad = concat([zeros((4, ), dtype="int32"), pad], axis=0)
                unsqueezed_dim = [2, 3]
                x = unsqueeze(x, axes=unsqueezed_dim)
            elif x_dim == 4:
                pad = concat([pad, zeros((2, ), dtype="int32")], axis=0)
                unsqueezed_dim = [1]
                x = unsqueeze(x, axes=unsqueezed_dim)
    else:
        if data_format in ["NCL", "NCHW", "NCDHW"]:
            data_format = "NCDHW"
            if x_dim == 3:
                pad = [0, 0, 0, 0] + pad
                unsqueezed_dim = [3, 4]
                x = unsqueeze(x, axes=unsqueezed_dim)
            elif x_dim == 4:
                pad = pad + [0, 0]
                unsqueezed_dim = [2]
                x = unsqueeze(x, axes=unsqueezed_dim)
        elif data_format in ["NLC", "NHWC", "NDHWC"]:
            data_format = "NDHWC"
            if x_dim == 3:
                pad = [0, 0, 0, 0] + pad
                unsqueezed_dim = [2, 3]
                x = unsqueeze(x, axes=unsqueezed_dim)
            elif x_dim == 4:
                pad = pad + [0, 0]
                unsqueezed_dim = [1]
                x = unsqueeze(x, axes=unsqueezed_dim)

    if in_dygraph_mode():
        if isinstance(pad, Variable):
            pad = pad.numpy()
        out = core.ops.pad3d(x, "paddings", pad, "mode", mode, "value", value,
                             "data_format", data_format, "name", name)
    else:
        attrs = {'mode': mode, 'value': value, 'data_format': data_format}
        inputs = {'X': [x]}
        if isinstance(pad, Variable):
            inputs['Paddings'] = [pad]
            attrs['paddings'] = []
        else:
            attrs['paddings'] = pad

        helper = LayerHelper('pad3d', **locals())

        dtype = helper.input_dtype(input_param_name='input')
        out = helper.create_variable_for_type_inference(dtype)
        helper.append_op(
            type='pad3d', inputs=inputs, outputs={"Out": out}, attrs=attrs)

    if len(unsqueezed_dim) != 0:
        out = squeeze(out, axes=unsqueezed_dim)

    return out


def cosine_similarity(x1, x2, axis=1, eps=1e-8):
    """
    Compute cosine similarity between x1 and x2 along axis.

    Parameters:
        x1 (Tensor): First input. float32/double.
        x2 (Tensor): Second input. float32/double.
        axis (int): Dimension of vectors to compute cosine similarity. Default is 1.
        eps(float): Small value to avoid division by zero. Default is 1e-8.
                    
    Returns: a Tensor representing cosine similarity between x1 and x2 along axis.
    Return Type: Tensor

    Examples:
        .. code-block:: text
            Case 0:
                x1 = [[0.8024077  0.9927354  0.27238318 0.8344984 ]
                     [0.48949873 0.5797396  0.65444374 0.66510963]
                     [0.1031398  0.9614342  0.08365563 0.6796464 ]
                     [0.10760343 0.7461209  0.7726148  0.5801006 ]]
                x2 = [[0.62913156 0.1536727  0.9847992  0.04591406]
                     [0.9098952  0.15715368 0.8671125  0.3156102 ]
                     [0.4427798  0.54136837 0.5276275  0.32394758]
                     [0.3769419  0.8535014  0.48041078 0.9256797 ]]
                axis = 1
                eps = 1e-8
                Out: [0.5275037  0.8368967  0.75037485 0.9245899]

    Code Examples:
        .. code-block:: python
            import paddle
            import paddle.nn as nn
            import numpy as np
            paddle.disable_static()

            np.random.seed(0)
            x1 = np.random.rand(2,3)
            x2 = np.random.rand(2,3)
            x1 = paddle.to_tensor(x1)
            x2 = paddle.to_tensor(x2)
            result = paddle.nn.functional.cosine_similarity(x1, x2, axis=0)
            print(result.numpy())
            # [0.99806249 0.9817672  0.94987036]
            
    """
    w12 = sum(elementwise_mul(x1, x2), axis=axis)
    w1 = sum(elementwise_mul(x1, x1), axis=axis)
    w2 = sum(elementwise_mul(x2, x2), axis=axis)
    n12 = sqrt(clip(w1 * w2, min=eps * eps))
    cos_sim = w12 / n12
    return cos_sim
