/**
 * @license
 * Copyright 2023 Google LLC.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * =============================================================================
 */
/// <amd-module name="@tensorflow/tfjs-backend-wasm/dist/kernels/Dilation2DBackpropInput" />
import { Dilation2DAttrs, KernelConfig, Tensor3D, Tensor4D, TensorInfo } from '@tensorflow/tfjs-core';
import { BackendWasm } from '../backend_wasm';
export declare function dilation2DBackpropInput(args: {
    inputs: {
        x: Tensor4D;
        filter: Tensor3D;
        dy: Tensor4D;
    };
    attrs: Dilation2DAttrs;
    backend: BackendWasm;
}): TensorInfo;
export declare const dilation2DBackpropInputConfig: KernelConfig;
