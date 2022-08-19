(config) => {
  config.logger.info('origin called');
  config.state.requests = (config.state.requests || 0) + 1;
  return {
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      count: config.state.requests,
    }),
  };
}
