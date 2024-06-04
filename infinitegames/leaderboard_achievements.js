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

async function fetchLeaderboard() {

  const response = await getLeaderboard();
  console.log(response);
  const leaderboard = await response.json();
  displayLeaderboard(leaderboard);

}

// implement in gameOver  function

async function getLeaderboard() {
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


function saveAchievements() {

  localStorage.setItem('achievements', JSON.stringify(Achievements));

  const a = new URLSearchParams(window.location.href);

  if (!a.get('userId')) return;

  const gameRequestId = a.get('gameRequestId');
  //POST
  // https://rzzuxqt0hi.execute-api.eu-central-1.amazonaws.com/Prod/api/telegram-game/user-data?userId=190933907&gameId=infinitewar

  fetch(`https://rzzuxqt0hi.execute-api.eu-central-1.amazonaws.com/Prod/api/telegram-game/user-data?userId=190933907&gameId=NachoBlaster`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(data => {
      achievements = JSON.stringify(Achievements);
      console.log('Success:', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function saveUnlocks() {
  localStorage.setItem('NachoBlasterModesUnlocked', JSON.stringify(modesUnlocked));
  localStorage.setItem('NachoBlasterAchievements', JSON.stringify(Achievements));

}

function loadAchievements() {
  const savedAchievements = localStorage.getItem('achievements');
  if (savedAchievements) {
    Object.assign(Achievements, JSON.parse(savedAchievements));
  }
}


function loadUnlocks() {
  const savedUnlocks = localStorage.getItem('NachoBlasterModesUnlocked');
  const achievements = localStorage.getItem('NachoBlasterAchievements');

  if (savedUnlocks) {
    modesUnlocked = JSON.parse(savedUnlocks);
    document.getElementById('normalButton').disabled = !modesUnlocked.normal;
    document.getElementById('hardButton').disabled = !modesUnlocked.hard;
  }
}






function displayLeaderboard(leaderboard) {
  const leaderboardContainer = document.getElementById('leaderboard');
  leaderboardContainer.innerHTML = '<h2>Leaderboard</h2><ol id="leaderboard-list"></ol>';
  const leaderboardList = document.getElementById('leaderboard-list');

  leaderboard.forEach(entry => {
    const listItem = document.createElement('li');
    listItem.textContent = `${entry.position}. ${entry.user.first_name} ${entry.user.last_name || ''} - ${entry.score}`;
    leaderboardList.appendChild(listItem);
  });

  document.getElementById('leaderboard-container').style.display = 'block';
  document.getElementById('coins').textContent = coins;
}
