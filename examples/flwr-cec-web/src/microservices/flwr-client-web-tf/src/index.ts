import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-wasm';
import { setWasmPaths } from '@tensorflow/tfjs-backend-wasm';

var times = []
declare var vpod: { env: { [key: string]: string }, location: { [key: string]: string } };

/**
 * Costruisce l'URL per accedere al dataset.
 */
const getDatasetURL = (dataset: string, distribution: string, chunkSize: number): string => {
    let dataServer = vpod.env.DATASET_SERVER ?? vpod.location.origin;
    return `${dataServer}/dataset/${dataset}/train/${distribution}/${chunkSize}`;
};

/**
 * Recupera e prepara il dataset da un URL.
 */
async function fetchAndPrepareDataset(datasetURL: string, normalize = true): Promise<{ images: tf.Tensor, labels: tf.Tensor }> {
    const response = await fetch(datasetURL);
    if (!response.ok) {
        throw new Error(`Failed to fetch dataset from ${datasetURL}`);
    }
    const dataObj = JSON.parse(await response.json());

    // Debug: Ispeziona l'oggetto JSON restituito
    console.log('Data Object:', dataObj);

    // Verifica la presenza delle proprietà
    if (!dataObj.data || !dataObj.data.images || !dataObj.data.labels) {
        throw new Error("The dataset JSON structure is invalid or missing required properties.");
    }

    // Converti le immagini e le etichette in tensori
    let images = dataObj.data.images as number[][];
    let labels = dataObj.data.labels as number[];

    if (normalize) {
        images = images.map(image => image.map(v => (v / 255.0 - 0.1307) / 0.3081)); // Normalizzazione standard
    }

    const numImages = labels.length;
    const imageSize = dataObj.shape[0]; // Dovrebbe essere 784

    // Assicura che le immagini abbiano la forma corretta [numImages, 784]
    const imagesTensor = tf.tensor2d(images, [numImages, imageSize], 'float32');
    const labelsTensor = tf.tensor1d(labels, 'float32');

    return { images: imagesTensor, labels: labelsTensor };
}

/**
 * Classe per definire e gestire il modello DNN.
 */
class DNN {
    model: tf.Sequential;

    constructor(inputSize: number, hiddenSize: number, numClasses: number) {
        this.model = tf.sequential();
        
        // Definizione del modello
        this.model.add(tf.layers.dense({
            units: hiddenSize,
            inputShape: [inputSize],
            activation: 'relu'
        }));

        this.model.add(tf.layers.dense({
            units: hiddenSize,
            activation: 'relu'
        }));

        this.model.add(tf.layers.dense({
            units: numClasses,
            activation: 'softmax'
        }));

        // Compilazione del modello con ottimizzatore e funzione di perdita
        this.model.compile({
            optimizer: tf.train.adam(),
            loss: 'sparseCategoricalCrossentropy',
            metrics: ['accuracy']
        });
    }

    // Metodo per ottenere i parametri del modello
    getParameters() {
        return this.model.getWeights().map(weight => weight.arraySync());
    }

    // Nuovo metodo per impostare i parametri del modello
    setParameters(weights: any) {
        const tensors = weights.map(w => tf.tensor(w));
        this.model.setWeights(tensors);
    }

    // Metodo per il training del modello
    async fit(trainData: { images: tf.Tensor, labels: tf.Tensor }, epochs = 10) {
        console.log("Training model...");
        const { images: trainX, labels: trainY } = trainData;

        const history = await this.model.fit(trainX, trainY, {
            epochs: epochs,
            batchSize: 64,
            validationSplit: 0.2,
            shuffle: true
        });
        console.log("Training completed.", history);
        trainX.dispose();
        trainY.dispose();

        return history;
    }

    async evaluate(testData: { images: tf.Tensor, labels: tf.Tensor }) {
        const { images: trainX, labels: trainY } = testData;
        const evalResult = await this.model.evaluate(trainX, trainY, {batchSize: 64});
        if (!Array.isArray(evalResult) || evalResult.length !== 2) {
            throw new Error("Unexpected evaluation result structure.");
        }
        const loss = evalResult[0]?.dataSync()[0];
        const accuracy = evalResult[1]?.dataSync()[0];
        return { loss, accuracy, length: 1000 };
    }
}

export const getParameters = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
    let parameters = model.getParameters();
    console.log("Parameters:", parameters);
    return {"params": parameters};
  }

var currentRound = 0;

export const fit = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
    let modelWeights = body.modelWeights || null

    await model.setParameters(modelWeights);

    const datasetURL = getDatasetURL('mnist', 'iid', 600);
    const data = await fetchAndPrepareDataset(datasetURL);

    await model.fit(data, 5);

    // Get loss
    // const { loss } = await model.evaluate(data);
    // fetch('vpod://main/onRoundEnd', { method: "POST", headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ y: loss, x: currentRound + 1, totalEpochs: currentRound + 1 }) });
    // currentRound++;

    let parameters = model.getParameters();

    return {'weights': parameters, 'length': 1000};
}

export const evaluate = async (body: RunTrainBody, params: GenericObjString, headers: GenericObjString): Promise<any> => {
    const datasetURL = getDatasetURL('mnist', 'iid', 600);
    const data = await fetchAndPrepareDataset(datasetURL);
    return await model.evaluate(data);
  }

async function main() {
    await tf.setBackend('wasm');
    console.log("TF Backend:", tf.getBackend());
}

console.log("Client TF loading...");
setWasmPaths('dist/');
var model = new DNN(784, 200, 100);
main().catch(err => console.error(err));

console.log("Client TF loaded.");

