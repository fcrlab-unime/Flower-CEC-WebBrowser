
import { Cifar10Data } from './datasets/cifar10';
import { MnistData } from './datasets/mnist';
import { Float32Concat } from './utils';
import * as ort from 'onnxruntime-web/training';

declare var vpod: {env: {[key: string]: string}, location: {[key: string]: string}};

// INIT
var trainset: Cifar10Data | MnistData;
var session = null;
var currentRound = 0;
var personalRound = 0;
let totalEpochs = 0;
var defaultValues: DefaultValues = {
  distribution: "iid",
  chunkSize: 1000,
  batchSize: 64,
}
var retrieveDatasetPromise: Promise<void>;
var initializationPromise: Promise<void>;
var lastRoundLoss = 0;

export const setDefaultParams = async (body: InitSessionBody, params: GenericObjString, headers: GenericObjString): Promise<DefaultValues> => {
  defaultValues = {
    distribution: body.distribution == "unbalanced" ? "non-iid" : "iid",
    chunkSize: body.chunkSize || 1000,
    batchSize: body.batchSize || 64,
  }
  return defaultValues;
}

const initSession = async (dataset: string, batchSize: number, chunkSize: number, distribution: string): Promise<string> => {
  reset();
  initializationPromise = initAsyncSession(dataset, distribution, chunkSize, batchSize);
  console.log("Session Initialized")
  return "Session Initialized";
}

async function initAsyncSession(dataset, distribution, chunkSize, batchSize): Promise<void> {
  const response = await fetch(`${vpod.env.MODEL_SERVER}/${dataset}/shapes.json`)
  const shapes = await response.json()

  console.log(`${vpod.env.MODEL_SERVER}/${dataset}/shapes.json`, shapes)

  let datasetURL = getDatasetURL(dataset, distribution, chunkSize)
  if (dataset === 'mnist') {
    trainset = new MnistData(batchSize, datasetURL, shapes)
  } else {
    trainset = new Cifar10Data(batchSize, datasetURL, shapes)
  }
  retrieveDatasetPromise = trainset.getData(true)

  session = await loadTrainingSession(vpod.env.MODEL_SERVER, dataset)
  console.log('[CLIENT] loaded dataset: ', dataset)
  console.log('[CLIENT] loaded chunk size: ', chunkSize)
  console.log('[CLIENT] loaded batch size: ', batchSize)
  console.log('[CLIENT] loaded distribution: ', distribution)
  return;
}

async function loadTrainingSession(modelServer: string, dataset: dataset): Promise<ort.TrainingSession> {
  const chkptPath = `${modelServer}/${dataset}/checkpoint`;
  const trainingPath = `${modelServer}/${dataset}/training_model.onnx`;
  const optimizerPath = `${modelServer}/${dataset}/optimizer_model.onnx`;
  const evalPath = `${modelServer}/${dataset}/eval_model.onnx`;

  const createOptions: ort.TrainingSessionCreateOptions = {
    checkpointState: chkptPath,
    trainModel: trainingPath,
    evalModel: evalPath,
    optimizerModel: optimizerPath,
  };
  try {
    const session = await ort.TrainingSession.create(createOptions);
    return session;
  } catch (err) {
    throw err;
  }
}

export const fit = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
  let modelWeights = body.modelWeights || null
  if (modelWeights) {
    await setParams(modelWeights)
  }
  
  if (initializationPromise) {
    await initializationPromise;
    initializationPromise = null;
  }
  if (retrieveDatasetPromise) {
    await retrieveDatasetPromise;
  }

  let avgEpochLoss = 0;
  let epochLoss = 0;
  for (let epoch = 0; epoch < numEpochs; epoch++) {
    epochLoss = await runTrainingEpoch(session, trainset);
    avgEpochLoss += epochLoss
    console.log('[CLIENT] Epoch loss ', epoch+1 ," (Total epochs:", totalEpochs, "):", epochLoss);
    totalEpochs++
    fetch('vpod://main/onEpochEnd', { method: "POST", headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ y: epochLoss, x: totalEpochs }) });
  }
  let roundLosses = avgEpochLoss / numEpochs
  lastRoundLoss = roundLosses
  fetch('vpod://main/onRoundEnd', { method: "POST", headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ y: roundLosses, x: currentRound + 1, totalEpochs }) });

  currentRound++;

  let weights = await getParams();

  let aggregateBody = {
    weights: Object.keys(weights).map((key) => weights[key]),
    length: trainset.actualTrainLength
  }

  retrieveDatasetPromise = trainset.getData(true);
  personalRound++;
  return aggregateBody;
}

export const evaluate = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
  return {
    'loss': lastRoundLoss,
    'length': trainset.actualTrainLength
  }
}

async function runTrainingEpoch(session: ort.TrainingSession, dataSet: Cifar10Data | MnistData): Promise<number> {

  let batchNum = 0;
  let runningLoss = 0;

  for await (const batch of dataSet.trainingBatches()) {
    ++batchNum;
    const feeds = { input: batch.data, labels: batch.labels };
    const results = await session.runTrainStep(feeds);
    const lossNodeName = Object.keys(results).find((key) => key.includes("loss"));
    let rawLoss = results[lossNodeName].data as unknown as string;

    const loss = parseFloat(rawLoss);
    runningLoss += loss;

    await session.runOptimizerStep();
    await session.lazyResetGrad();
  }
  let epochLoss = runningLoss / batchNum;
  return epochLoss
}

export const getParameters = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
  if (initializationPromise) {
    await initializationPromise;
    initializationPromise = null;
  }
  let parameters = await getParams();
  return {"params": Object.keys(parameters).map((key) => parameters[key])};
}

const getParams = async (): Promise<Weights> => {
  const weights = await session.getContiguousParameters(true);
  const shapes = trainset.shapes
  const weights_obj = {}
  let offset = 0

  let next_offset = 0

  for (let i = 0; i < shapes.length; i++) {
    next_offset += shapes[i].shape.reduce((a: number, b: number) => a * b, 1)
    weights_obj[shapes[i]['name']] = Array.from<Float32Array>(weights.data.slice(offset, next_offset))
    offset = next_offset
  }

  return weights_obj
}

export const setParameters = async (body: any, params: GenericObjString, headers: GenericObjString): Promise<any> => {
  let weights = body.weights
  let result = await setParams(weights)
  return {"message": result}
}

export const setParams = async (weights: Weights): Promise<string> => {
  let new_weights = new Float32Array()
  const shapes = trainset.shapes

  for (let i = 0; i < shapes.length; i++) {
    new_weights = Float32Concat(new_weights, weights[i])
  }
  await session.loadParametersBuffer(new Uint8Array(new_weights.buffer), true)
  new_weights = null
  return "Weights set"
}

const getDatasetURL = (dataset: string, distribution: string, chunkSize: number) => {
  let dataServer = vpod.env.DATASET_SERVER ?? vpod.location.origin;
  return `${dataServer}/dataset/${dataset}/train/${distribution}/${chunkSize}`;
}

const reset = () => {
  fetch('vpod://main/resetCharts');
  session = null;
  currentRound = 0;
  personalRound = 0;
  totalEpochs = 0;
}

function getHeader(headers: any, headerName: string): string | undefined{
  for (let key in headers) {
    if (key.toLowerCase() === headerName.toLowerCase()) {
      return headers[key];
    }
  }
  return undefined;
}

console.log("[CLIENT] Loaded.")
initSession("mnist", 64, 1000, "iid")
var numEpochs = 2;