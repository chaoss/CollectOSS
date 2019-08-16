/* tslint:disable */
import router from '@/router'
import Vue from 'vue';
import { VL_ONLY_GUIDE_CONFIG } from 'vega-lite/build/src/guide';
export default {
  mutateCache(state: any, payload: any) {
    Vue.set(state.cache, payload.property, payload.with)
  },
  mutate(state: any, payload: any) {
    Vue.set(state, payload.property, payload.with);
  },
}