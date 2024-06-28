# Infinite Package Manager

A package manager for code generation that allows you to utilize modular programming to mix and match elements from different code bases. Used as the backend for infinite games. 


# Features

- takes a list of directories and deploys common libraries
- libraries handle user login, leaderboard, and coin logic
- aggregates the data behind the git repos in these directories, sorts and shows it
- takes the deployed version of the apps and snapshots them, then makes a web page which shows links to all the working ones
- shows user analytics including play time and rating for the games (in progress)


![Infinite Game Activity](/images/commit_activity.png)

# Auxillary Libraries

**Text-to-3d toolchain** - takes text and generates glb files that can be integrated

**Make me 8 bit** - takes image input (can be automated AI tooling) and converts to 8bit style transparent PNGs, sometimes with explicit color coding  

**8bit sound** - Similar concept for sound generation including custom composed sound trakcs

# Architecture 

<img width="811" alt="Screenshot 2024-06-28 at 14 53 48" src="https://github.com/fractastical/ipm/assets/589191/84523954-296b-4c96-bbc9-f4a70b186ea4">


# Goals 

Infinite extensible play probably with one core game that has a dynamic modding community and ability to easly port game logic between different game engines.

# Under development 

- Currently "push" based (i.e. code is packaged and pushed. Should also be a pull version with better versionoing so that anyone can integrate this code snippets)
- Coin / web3 logic


Other games that are not currently included here:  Hunt the Golem, Zeus
