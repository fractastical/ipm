const baseUrl = 'https://rzzuxqt0hi.execute-api.eu-central-1.amazonaws.com/Prod/api';
let gameSessionId = '';

function startGamingSessionApi() {
  const a = new URLSearchParams(window.location.href);

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

function endGameSessionApi(score) {
  const a = new URLSearchParams(window.location.href);

  const gameRequestId = a.get('gameRequestId');

  const inMsgId = a.get('inMsgId').split('#')[0];
  const userId = a.get('userId');

  fetch(`${baseUrl}/telegram-game/end-game?gameRequestId=${gameRequestId}&gameSessionId=${gameSessionId}&inMsgId=${inMsgId}&userId=${userId}&score=${score}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getLeaderboard() {

  return fetch(`${baseUrl}/telegram-game/leaderboard`, {
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