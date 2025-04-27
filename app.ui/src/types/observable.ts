

export interface Subscription {
    unsubscribe(): void;
  }

  export const EmptySubscription: Subscription = {
    unsubscribe: () => {}
  };
