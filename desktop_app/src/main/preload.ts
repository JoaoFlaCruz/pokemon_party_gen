import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("pokemonPartyGen", {
  contractVersion: "fixture-1"
});
