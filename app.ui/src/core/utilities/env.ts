



export const BasePath = import.meta.env.VITE_BASE_PATH
export const ApiPath = import.meta.env.VITE_API_PATH

export const RawWebsocketPath = import.meta.env.VITE_WS_PATH

export const WebSocketBasePath = RawWebsocketPath.startsWith('ws')
  ? RawWebsocketPath
  : `${window.location.protocol === 'https:' ? 'wss://' : 'ws://'}${window.location.host}${import.meta.env.VITE_WS_PATH}`;

console.log("API:", ApiPath);
console.log("WS:", WebSocketBasePath);





// check if we are in development mode
export const isDevMode = (): boolean => {
    return import.meta.env.MODE == 'development';
  };


