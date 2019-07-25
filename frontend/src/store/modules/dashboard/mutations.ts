/* tslint:disable */
import router from '@/router'
import Vue from 'vue';
export default {
  mutateCache(state: any, payload: any) {
    Vue.set(state.cache, payload.property, payload.with)
  },
  mutate(state: any, payload: any) {
    Vue.set(state, payload.property, payload.with);
  },
}