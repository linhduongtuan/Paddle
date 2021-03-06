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
from __future__ import print_function
import numpy as np
from ..fluid.layer_helper import LayerHelper
from ..fluid.data_feeder import check_variable_and_dtype, check_type, check_dtype
from ..fluid import core, layers

# TODO: define searching & indexing functions of a tensor  
from ..fluid.layers import argmin  #DEFINE_ALIAS
from ..fluid.layers import has_inf  #DEFINE_ALIAS
from ..fluid.layers import has_nan  #DEFINE_ALIAS
from ..fluid.layers import topk  #DEFINE_ALIAS

__all__ = [
    'argmax',
    'argmin',
    'argsort',
    'has_inf',
    'has_nan',
    'masked_select',
    'topk',
    'where',
    'index_select',
    'nonzero',
    'sort',
    'index_sample',
]

from paddle.common_ops_import import *


def argsort(x, axis=-1, descending=False, name=None):
    """
	:alias_main: paddle.argsort
	:alias: paddle.argsort,paddle.tensor.argsort,paddle.tensor.search.argsort

    This OP sorts the input along the given axis, and returns the corresponding index tensor for the sorted output values. The default sort algorithm is ascending, if you want the sort algorithm to be descending, you must set the :attr:`descending` as True.

    Args:
        x(Tensor): An input N-D Tensor with type float32, float64, int16,
            int32, int64, uint8.
        axis(int, optional): Axis to compute indices along. The effective range
            is [-R, R), where R is Rank(x). when axis<0, it works the same way
            as axis+R. Default is 0.
        descending(bool, optional) : Descending is a flag, if set to true,
            algorithm will sort by descending order, else sort by
            ascending order. Default is false.
        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.

    Returns:
        Tensor: sorted indices(with the same shape as ``x``
        and with data type int64).

    Examples:
        .. code-block:: python
            import paddle
            import numpy as np
            
            paddle.disable_static()
            input_array = np.array([[[5,8,9,5],
                            [0,0,1,7],
                            [6,9,2,4]],
                            [[5,2,4,2],
                            [4,7,7,9],
                            [1,7,0,6]]]).astype(np.float32)
            x = paddle.to_variable(input_array)
            out1 = paddle.argsort(x=x, axis=-1)
            out2 = paddle.argsort(x=x, axis=0)
            out3 = paddle.argsort(x=x, axis=1)
            print(out1.numpy())
            #[[[0 3 1 2]
            #  [0 1 2 3]
            #  [2 3 0 1]]
            # [[1 3 2 0]
            #  [0 1 2 3]
            #  [2 0 3 1]]]
            print(out2.numpy())
            #[[[0 1 1 1]
            #  [0 0 0 0]
            #  [1 1 1 0]]
            # [[1 0 0 0]
            #  [1 1 1 1]
            #  [0 0 0 1]]]
            print(out3.numpy())
            #[[[1 1 1 2]
            #  [0 0 2 0]
            #  [2 2 0 1]]
            # [[2 0 2 0]
            #  [1 1 0 2]
            #  [0 2 1 1]]]
    """
    if in_dygraph_mode():
        _, ids = core.ops.argsort(x, 'axis', axis, 'descending', descending)
        return ids
    check_variable_and_dtype(
        x, 'x', ['float32', 'float64', 'int16', 'int32', 'int64', 'uint8'],
        'argsort')

    helper = LayerHelper("argsort", **locals())
    out = helper.create_variable_for_type_inference(
        dtype=x.dtype, stop_gradient=True)
    ids = helper.create_variable_for_type_inference(
        VarDesc.VarType.INT64, stop_gradient=True)
    helper.append_op(
        type='argsort',
        inputs={'X': x},
        outputs={'Out': out,
                 'Indices': ids},
        attrs={'axis': axis,
               'descending': descending})
    return ids


def argmax(input, axis=None, dtype=None, out=None, keepdims=False, name=None):
    """
	:alias_main: paddle.argmax
	:alias: paddle.argmax,paddle.tensor.argmax,paddle.tensor.search.argmax

    This OP computes the indices of the max elements of the input tensor's
    element along the provided axis.

    Args:
        input(Variable): An input N-D Tensor with type float32, float64, int16,
            int32, int64, uint8.
        axis(int, optional): Axis to compute indices along. The effective range
            is [-R, R), where R is Rank(input). when axis<0, it works the same way
            as axis+R. Default is None, it will use the last dim to select indices of max value.
        dtype(np.dtype|core.VarDesc.VarType|str): Data type of the output tensor which can
                    be int32, int64. The default value is None, and it will
                    return the int64 indices.
        out(Variable, optional): Optional output which can be any created 
            Variable that meets the requirements to store the result of operation.
            if out is None, a new Varibale will be create to store the result. Defalut is None.
        keepdims(bool, optional): Keep the axis that do the select max.
        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.

    Returns:
        Variable: A Tensor with data type int64.

    Examples:
        .. code-block:: python

            import paddle
            import paddle.fluid as fluid
            import numpy as np

            in1 = np.array([[[5,8,9,5],
                            [0,0,1,7],
                            [6,9,2,4]],
                            [[5,2,4,2],
                            [4,7,7,9],
                            [1,7,0,6]]])
            with fluid.dygraph.guard():
                x = fluid.dygraph.to_variable(in1)
                out1 = paddle.argmax(input=x, axis=-1)
                out2 = paddle.argmax(input=x, axis=0)
                out3 = paddle.argmax(input=x, axis=1)
                out4 = paddle.argmax(input=x, axis=2)
                out5 = paddle.argmax(input=x, axis=2, keepdims=True)
                print(out1.numpy())
                # [[2 3 1]
                #  [0 3 1]]
                print(out2.numpy())
                # [[0 0 0 0]
                #  [1 1 1 1]
                #  [0 0 0 1]]
                print(out3.numpy())
                # [[2 2 0 1]
                #  [0 1 1 1]]
                print(out4.numpy())
                # [[2 3 1]
                #  [0 3 1]]
                print(out5.numpy())
                #array([[[2],
                #        [3],
                #        [1]],
                #       [[0],
                #        [3],
                #        [1]]])
    """
    helper = LayerHelper("arg_max", **locals())
    var_dtype = None
    attrs = {}
    if dtype is not None:
        check_dtype(dtype, 'create data type', ['int32', 'int64'], 'arg_max')
        var_dtype = convert_np_dtype_to_dtype_(dtype)
        attrs["dtype"] = var_dtype
    else:
        var_dtype = VarDesc.VarType.INT64
    if out is None:
        out = helper.create_variable_for_type_inference(var_dtype)
    if axis is None:
        axis = -1
    attrs['keepdims'] = keepdims
    attrs['axis'] = axis
    helper.append_op(
        type='arg_max',
        inputs={'X': input},
        outputs={'Out': [out]},
        attrs=attrs)
    out.stop_gradient = True
    return out


def index_select(x, index, axis=0, name=None):
    """
	:alias_main: paddle.index_select
	:alias: paddle.tensor.index_select, paddle.tensor.search.index_select

    Returns a new tensor which indexes the ``input`` tensor along dimension ``axis`` using 
    the entries in ``index`` which is a Tensor. The returned tensor has the same number 
    of dimensions as the original ``x`` tensor. The dim-th dimension has the same 
    size as the length of ``index``; other dimensions have the same size as in the ``x`` tensor. 

    Args:
        x (Tensor): The input Tensor to be operated. The data of ``x`` can be one of float32, float64, int32, int64.
        index (Tensor): The 1-D Tensor containing the indices to index. The data type of ``index`` must be int32 or int64.
        axis (int, optional): The dimension in which we index. Default: if None, the ``axis`` is 0.
        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.

    Returns:
        Tensor: A Tensor with same data type as ``x``.
    
    Raises:
        TypeError: ``x`` must be a Tensor and the data type of ``x`` must be one of  float32, float64, int32 and int64.
        TypeError: ``index`` must be a Tensor and the data type of ``index`` must be int32 or int64.

    Examples:
        .. code-block:: python
            
            import paddle
            import numpy as np

            paddle.disable_static()  # Now we are in imperative mode
            data = np.array([[1.0, 2.0, 3.0, 4.0],
                             [5.0, 6.0, 7.0, 8.0],
                             [9.0, 10.0, 11.0, 12.0]])
            data_index = np.array([0, 1, 1]).astype('int32')

            x = paddle.to_tensor(data)
            index = paddle.to_tensor(data_index)
            out_z1 = paddle.index_select(x=x, index=index)
            #[[1. 2. 3. 4.]
            # [5. 6. 7. 8.]
            # [5. 6. 7. 8.]]
            out_z2 = paddle.index_select(x=x, index=index, axis=1)
            #[[ 1.  2.  2.]
            # [ 5.  6.  6.]
            # [ 9. 10. 10.]]
    """

    if in_dygraph_mode():
        return core.ops.index_select(x, index, 'dim', axis)

    helper = LayerHelper("index_select", **locals())
    check_variable_and_dtype(x, 'x', ['float32', 'float64', 'int32', 'int64'],
                             'paddle.tensor.search.index_select')
    check_variable_and_dtype(index, 'index', ['int32', 'int64'],
                             'paddle.tensor.search.index_select')

    out = helper.create_variable_for_type_inference(x.dtype)

    helper.append_op(
        type='index_select',
        inputs={'X': x,
                'Index': index},
        outputs={'Out': out},
        attrs={'dim': axis})
    return out


def nonzero(input, as_tuple=False):
    """
	:alias_main: paddle.nonzero
	:alias: paddle.nonzero,paddle.tensor.nonzero,paddle.tensor.search.nonzero

    Return a tensor containing the indices of all non-zero elements of the `input` 
    tensor. If as_tuple is True, return a tuple of 1-D tensors, one for each dimension 
    in `input`, each containing the indices (in that dimension) of all non-zero elements 
    of `input`. Given a n-Dimensional `input` tensor with shape [x_1, x_2, ..., x_n], If 
    as_tuple is False, we can get a output tensor with shape [z, n], where `z` is the 
    number of all non-zero elements in the `input` tensor. If as_tuple is True, we can get 
    a 1-D tensor tuple of length `n`, and the shape of each 1-D tensor is [z, 1].

    Args:
        inputs (Variable): The input tensor variable.
        as_tuple (bool): Return type, Tensor or tuple of Tensor.

    Returns:
        Variable. The data type is int64.

    Examples:
        .. code-block:: python
            import paddle
            import paddle.fluid as fluid
            import numpy as np

            data1 = np.array([[1.0, 0.0, 0.0],
                              [0.0, 2.0, 0.0],
                              [0.0, 0.0, 3.0]])
            data2 = np.array([0.0, 1.0, 0.0, 3.0])
            data3 = np.array([0.0, 0.0, 0.0])
            with fluid.dygraph.guard():
                x1 = fluid.dygraph.to_variable(data1)
                x2 = fluid.dygraph.to_variable(data2)
                x3 = fluid.dygraph.to_variable(data3)
                out_z1 = paddle.nonzero(x1)
                print(out_z1.numpy())
                #[[0 0]
                # [1 1]
                # [2 2]]
                out_z1_tuple = paddle.nonzero(x1, as_tuple=True)
                for out in out_z1_tuple:
                    print(out.numpy())
                #[[0]
                # [1]
                # [2]]
                #[[0]
                # [1]
                # [2]]
                out_z2 = paddle.nonzero(x2)
                print(out_z2.numpy())
                #[[1]
                # [3]]
                out_z2_tuple = paddle.nonzero(x2, as_tuple=True)
                for out in out_z2_tuple:
                    print(out.numpy())
                #[[1]
                # [3]]
                out_z3 = paddle.nonzero(x3)
                print(out_z3.numpy())
                #[]
                out_z3_tuple = paddle.nonzero(x3, as_tuple=True)
                for out in out_z3_tuple:
                    print(out.numpy())
                #[]                    
    """
    list_out = []
    shape = input.shape
    rank = len(shape)

    if in_dygraph_mode():
        outs = core.ops.where_index(input)
    else:
        outs = layers.where(input)

    if not as_tuple:
        return outs
    elif rank == 1:
        return tuple([outs])
    else:
        for i in range(rank):
            list_out.append(
                layers.slice(
                    outs, axes=[rank - 1], starts=[i], ends=[i + 1]))
        return tuple(list_out)


def sort(x, axis=-1, descending=False, name=None):
    """
	:alias_main: paddle.sort
	:alias: paddle.sort,paddle.tensor.sort,paddle.tensor.search.sort

    This OP sorts the input along the given axis, and returns the sorted output tensor. The default sort algorithm is ascending, if you want the sort algorithm to be descending, you must set the :attr:`descending` as True.

    Args:
        x(Tensor): An input N-D Tensor with type float32, float64, int16,
            int32, int64, uint8.
        axis(int, optional): Axis to compute indices along. The effective range
            is [-R, R), where R is Rank(x). when axis<0, it works the same way
            as axis+R. Default is 0.
        descending(bool, optional) : Descending is a flag, if set to true,
            algorithm will sort by descending order, else sort by
            ascending order. Default is false.
        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.
    Returns:
        Tensor: sorted tensor(with the same shape and data type as ``x``).
    Examples:
        .. code-block:: python
            import paddle
            import numpy as np
            
            paddle.disable_static()
            input_array = np.array([[[5,8,9,5],
                            [0,0,1,7],
                            [6,9,2,4]],
                            [[5,2,4,2],
                            [4,7,7,9],
                            [1,7,0,6]]]).astype(np.float32)
            x = paddle.to_variable(input_array)
            out1 = paddle.sort(x=x, axis=-1)
            out2 = paddle.sort(x=x, axis=0)
            out3 = paddle.sort(x=x, axis=1)
            print(out1.numpy())
            #[[[5. 5. 8. 9.]
            #  [0. 0. 1. 7.]
            #  [2. 4. 6. 9.]]
            # [[2. 2. 4. 5.]
            #  [4. 7. 7. 9.]
            #  [0. 1. 6. 7.]]]
            print(out2.numpy())
            #[[[5. 2. 4. 2.]
            #  [0. 0. 1. 7.]
            #  [1. 7. 0. 4.]]
            # [[5. 8. 9. 5.]
            #  [4. 7. 7. 9.]
            #  [6. 9. 2. 6.]]]
            print(out3.numpy())
            #[[[0. 0. 1. 4.]
            #  [5. 8. 2. 5.]
            #  [6. 9. 9. 7.]]
            # [[1. 2. 0. 2.]
            #  [4. 7. 4. 6.]
            #  [5. 7. 7. 9.]]]
    """
    if in_dygraph_mode():
        out, _ = core.ops.argsort(x, 'axis', axis, 'descending', descending)
        return out
    helper = LayerHelper("sort", **locals())
    out = helper.create_variable_for_type_inference(
        dtype=x.dtype, stop_gradient=False)
    ids = helper.create_variable_for_type_inference(
        VarDesc.VarType.INT64, stop_gradient=True)
    helper.append_op(
        type='argsort',
        inputs={'X': x},
        outputs={'Out': out,
                 'Indices': ids},
        attrs={'axis': axis,
               'descending': descending})
    return out


def where(condition, x, y, name=None):
    """
	:alias_main: paddle.where
	:alias: paddle.where,paddle.tensor.where,paddle.tensor.search.where

    Return a tensor of elements selected from either $x$ or $y$, depending on $condition$.

    .. math::

      out_i =
      \\begin{cases}
      x_i, \quad  \\text{if}  \\ condition_i \\  is \\ True \\\\
      y_i, \quad  \\text{if}  \\ condition_i \\  is \\ False \\\\
      \\end{cases}


    Args:
        condition(Variable): The condition to choose x or y.
        x(Variable): x is a Tensor Variable with data type float32, float64, int32, int64.
        y(Variable): y is a Tensor Variable with data type float32, float64, int32, int64.

        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.

    Returns:
        Variable: A Tensor with the same data dype as x. 

    Examples:
        .. code-block:: python

          import paddle
          import numpy as np
          import paddle.fluid as fluid

          x_i = np.array([0.9383, 0.1983, 3.2, 1.2]).astype("float32")
          y_i = np.array([1.0, 1.0, 1.0, 1.0]).astype("float32")

          with fluid.dygraph.guard():
              x = fluid.dygraph.to_variable(x_i)
              y = fluid.dygraph.to_variable(y_i)
              out = paddle.where(x>1, x, y)

          print(out.numpy())
          #out: [1.0, 1.0, 3.2, 1.2]
    """
    if not in_dygraph_mode():
        check_variable_and_dtype(condition, 'condition', ['bool'], 'where')
        check_variable_and_dtype(
            x, 'x', ['float32', 'float64', 'int32', 'int64'], 'where')
        check_variable_and_dtype(
            y, 'y', ['float32', 'float64', 'int32', 'int64'], 'where')

    x_shape = list(x.shape)
    y_shape = list(y.shape)
    if x_shape == y_shape:
        if in_dygraph_mode():
            return core.ops.where(condition, x, y)
        else:
            helper = LayerHelper("where", **locals())
            out = helper.create_variable_for_type_inference(dtype=x.dtype)

            helper.append_op(
                type='where',
                inputs={'Condition': condition,
                        'X': x,
                        'Y': y},
                outputs={'Out': [out]})
            return out
    else:
        cond_int = layers.cast(condition, x.dtype)
        cond_not_int = layers.cast(layers.logical_not(condition), x.dtype)
        out1 = layers.elementwise_mul(x, cond_int)
        out2 = layers.elementwise_mul(y, cond_not_int)
        out = layers.elementwise_add(out1, out2)
        return out


def index_sample(x, index):
    """
	:alias_main: paddle.index_sample
	:alias: paddle.index_sample,paddle.tensor.index_sample,paddle.tensor.search.index_sample

    **IndexSample Layer**

    IndexSample OP returns the element of the specified location of X, 
    and the location is specified by Index. 

    .. code-block:: text


                Given:

                X = [[1, 2, 3, 4, 5],
                     [6, 7, 8, 9, 10]]

                Index = [[0, 1, 3],
                         [0, 2, 4]]

                Then:

                Out = [[1, 2, 4],
                       [6, 8, 10]]

    Args:
        x (Variable): The source input tensor with 2-D shape. Supported data type is 
            int32, int64, float32, float64.
        index (Variable): The index input tensor with 2-D shape, first dimension should be same with X. 
            Data type is int32 or int64.

    Returns:
        output (Variable): The output is a tensor with the same shape as index.

    Examples:

        .. code-block:: python

            import paddle
            import paddle.fluid as fluid
            import numpy as np

            data = np.array([[1.0, 2.0, 3.0, 4.0],
                                [5.0, 6.0, 7.0, 8.0],
                                [9.0, 10.0, 11.0, 12.0]]).astype('float32')

            data_index = np.array([[0, 1, 2],
                                    [1, 2, 3],
                                    [0, 0, 0]]).astype('int32')

            target_data = np.array([[100, 200, 300, 400],
                                    [500, 600, 700, 800],
                                    [900, 1000, 1100, 1200]]).astype('int32')

            with fluid.dygraph.guard():
                x = fluid.dygraph.to_variable(data)
                index = fluid.dygraph.to_variable(data_index)
                target = fluid.dygraph.to_variable(target_data)

                out_z1 = paddle.index_sample(x, index)
                print(out_z1.numpy())
                #[[1. 2. 3.]
                # [6. 7. 8.]
                # [9. 9. 9.]]

                # Use the index of the maximum value by topk op
                # get the value of the element of the corresponding index in other tensors
                top_value, top_index = fluid.layers.topk(x, k=2)
                out_z2 = paddle.index_sample(target, top_index)
                print(top_value.numpy())
                #[[ 4.  3.]
                # [ 8.  7.]
                # [12. 11.]]

                print(top_index.numpy())
                #[[3 2]
                # [3 2]
                # [3 2]]

                print(out_z2.numpy())
                #[[ 400  300]
                # [ 800  700]
                # [1200 1100]]


    """
    helper = LayerHelper("index_sample", **locals())
    check_variable_and_dtype(x, 'x', ['float32', 'float64', 'int32', 'int64'],
                             'paddle.tensor.search.index_sample')
    check_variable_and_dtype(index, 'index', ['int32', 'int64'],
                             'paddle.tensor.search.index_sample')
    out = helper.create_variable_for_type_inference(dtype=x.dtype)

    helper.append_op(
        type='index_sample',
        inputs={'X': x,
                'Index': index},
        outputs={'Out': out})
    return out


def masked_select(x, mask, name=None):
    """
    This OP Returns a new 1-D tensor which indexes the input tensor according to the ``mask``
    which is a tensor with data type of bool.

    Args:
        x (Tensor): The input Tensor, the data type can be int32, int64, float32, float64. 
        mask (Tensor): The Tensor containing the binary mask to index with, it's data type is bool.
        name(str, optional): The default value is None. Normally there is no
            need for user to set this property. For more information, please
            refer to :ref:`api_guide_Name`.

    Returns: A 1-D Tensor which is the same data type  as ``x``.
    
    Raises:
        TypeError: ``x`` must be a Tensor and the data type of ``x`` must be one of  float32, float64, int32 and int64.
        TypeError: ``mask`` must be a Tensor and the data type of ``mask`` must be bool.

    Examples:

        .. code-block:: python

            import paddle
            import numpy as np
            
            paddle.disable_static()
            data = np.array([[1.0, 2.0, 3.0, 4.0],
                                [5.0, 6.0, 7.0, 8.0],
                                [9.0, 10.0, 11.0, 12.0]]).astype('float32')
            
            mask_data = np.array([[True, False, False, False],
                            [True, True, False, False],
                            [True, False, False, False]]).astype('bool')
            x = paddle.to_tensor(data)
            mask = paddle.to_tensor(mask_data)
            out = paddle.masked_select(x, mask)
            #[1.0 5.0 6.0 9.0]
    """

    if in_dygraph_mode():
        return core.ops.masked_select(x, mask)

    helper = LayerHelper("masked_select", **locals())
    check_variable_and_dtype(x, 'x', ['float32', 'float64', 'int32', 'int64'],
                             'paddle.tensor.search.mask_select')
    check_variable_and_dtype(mask, 'mask', ['bool'],
                             'paddle.tensor.search.masked_select')
    out = helper.create_variable_for_type_inference(dtype=x.dtype)
    helper.append_op(
        type='masked_select', inputs={'X': x,
                                      'Mask': mask}, outputs={'Y': out})
    return out
