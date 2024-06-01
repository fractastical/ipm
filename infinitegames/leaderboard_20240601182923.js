const baseUrl = 'https://rzzuxqt0hi.execute-api.eu-central-1.amazonaws.com/Prod/api';
let gameSessionId = '';

// outside dependencies should just be the score variable

// implement in startGame function
function startGamingSessionApi() {
  const a = new URLSearchParams(window.location.href);

  if (!a.get('userId')) return;

  const gameRequestId = a.get('gameRequestId');

  fetch(`${baseUrl}/telegram-game/start-game?gameRequestId=${gameRequestId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      gameSessionId = data;
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// implement in gameOver function

function endGameSessionApi(score) {
  const a = new URLSearchParams(window.location.href);
  if (!a.get('userId')) return;

  const gameRequestId = a.get('gameRequestId');

  const inMsgId = a.get('inMsgId').split('#')[0];
  const userId = a.get('userId');

  return fetch(`${baseUrl}/telegram-game/end-game?gameRequestId=${gameRequestId}&gameSessionId=${gameSessionId}&inMsgId=${inMsgId}&userId=${userId}&score=${score}`, {
        method: 'POST'
    })
    .then(response => console.log('Success:', data))
    .catch(error => {
        console.error('Error:', error);
    });
}

// implement in gameOver  function

function getLeaderboard() {
  const a = new URLSearchParams(window.location.href);
  if (!a.get('userId')) return;

  return fetch(`${baseUrl}/telegram-game/leaderboard?userId=${a.get('userId')}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success leaderboard fetch:', data);
      return data;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getActivityStats() {
  const a = new URLSearchParams(window.location.href);
  if (!a.get('userId')) return;

  return fetch(`${baseUrl}/telegram-game/activity-stats`, {
    method: 'GET'
  }).then(s => s.json())
  .then(data => {
    console.log('Success activity stats fetch:', data);
    return data;
  })
  .catch(error => {
    console.error('Error:', error);
  })
}
