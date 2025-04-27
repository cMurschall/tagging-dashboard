import { onBeforeUnmount, ref } from "vue";
import { Observable } from "../observable";


export const useObservable = <T>(obs: Observable<T>) => {
  const state = ref<T>(obs.getValue() as T);

  const Subscription = obs.subscribe((value: T) => {
    state.value = value;
  });

  onBeforeUnmount(() => {
    Subscription.unsubscribe();
  })

  return state;

}

