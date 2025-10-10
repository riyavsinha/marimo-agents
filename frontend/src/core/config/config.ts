/* Copyright 2024 Marimo. All rights reserved. */
import { atom, useAtom, useAtomValue, useSetAtom } from "jotai";
import { merge } from "lodash-es";
import { OverridingHotkeyProvider } from "../hotkeys/hotkeys";
import { type Platform, resolvePlatform } from "../hotkeys/shortcuts";
import { Logger } from "../../utils/Logger";
import { API } from "../network/api";
import { store } from "../state/jotai";
import {
  type AppConfig,
  defaultUserConfig,
  parseAppConfig,
  type UserConfig,
} from "./config-schema";

/**
 * Atom for storing the user config.
 */
export const userConfigAtom = atom<UserConfig>(defaultUserConfig());

export const configOverridesAtom = atom<{}>({});

export const resolvedMarimoConfigAtom = atom<UserConfig>((get) => {
  const overrides = get(configOverridesAtom);
  const userConfig = get(userConfigAtom);
  return merge({}, userConfig, overrides);
});

export const autoInstantiateAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).runtime.auto_instantiate;
});

export const hotkeyOverridesAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).keymap.overrides ?? {};
});

export const platformAtom = atom<Platform>(resolvePlatform());

export const hotkeysAtom = atom((get) => {
  const overrides = get(hotkeyOverridesAtom);
  const platform = get(platformAtom);
  return new OverridingHotkeyProvider(overrides, { platform });
});

export const autoSaveConfigAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).save;
});

export const aiAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).ai;
});

export const serverConfigAtom = atom(async () => {
  try {
    const response = await API.get<{
      disable_home_page: boolean;
      disable_terminal: boolean;
      disabled_panels: string[];
    }>("/kernel/server_config");
    return {
      disable_home_page: response?.disable_home_page ?? false,
      disable_terminal: response?.disable_terminal ?? false,
      disabled_panels: response?.disabled_panels ?? [],
      browser: "default",
      follow_symlink: false,
    };
  } catch (error) {
    Logger.warn("Failed to fetch server config:", error);
    return {
      disable_home_page: false,
      disable_terminal: false,
      disabled_panels: [],
      browser: "default",
      follow_symlink: false,
    };
  }
});

export const completionAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).completion;
});

export const keymapPresetAtom = atom((get) => {
  return get(resolvedMarimoConfigAtom).keymap.preset;
});

/**
 * Returns the user config.
 */
export function useUserConfig() {
  return useAtom(userConfigAtom);
}

export function useResolvedMarimoConfig() {
  return [
    useAtomValue(resolvedMarimoConfigAtom),
    useSetAtom(userConfigAtom),
  ] as const;
}

export function getResolvedMarimoConfig() {
  return store.get(resolvedMarimoConfigAtom);
}

export function useServerConfig() {
  return useAtomValue(serverConfigAtom);
}

export const aiEnabledAtom = atom<boolean>((get) => {
  return isAiEnabled(get(resolvedMarimoConfigAtom));
});

export const editorFontSizeAtom = atom<number>((get) => {
  return get(resolvedMarimoConfigAtom).display.code_editor_font_size;
});

export const localeAtom = atom<string | null | undefined>((get) => {
  return get(resolvedMarimoConfigAtom).display.locale;
});

export function isAiEnabled(config: UserConfig) {
  return (
    Boolean(config.ai?.models?.chat_model) ||
    Boolean(config.ai?.models?.edit_model) ||
    Boolean(config.ai?.models?.autocomplete_model)
  );
}

/**
 * Atom for storing the app config.
 */
export const appConfigAtom = atom<AppConfig>(parseAppConfig({}));

/**
 * Returns the app config.
 */
export function useAppConfig() {
  return useAtom(appConfigAtom);
}

export function useSetAppConfig() {
  return useSetAtom(appConfigAtom);
}

export function getAppConfig() {
  return store.get(appConfigAtom);
}

export const appWidthAtom = atom((get) => get(appConfigAtom).width);
