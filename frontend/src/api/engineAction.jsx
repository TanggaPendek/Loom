import { sendToBackend } from './client';

export const runEngine = () => sendToBackend("run");
export const stopEngine = () => sendToBackend("stop");
export const forceStop = () => sendToBackend("force_stop");