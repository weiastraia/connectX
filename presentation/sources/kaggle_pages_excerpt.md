# Kaggle Connect X 页面摘录（2026-10-28 通过 Kaggle 页面接口读取）

来源：https://www.kaggle.com/competitions/connectx （Evaluation、Environment Rules 两节的原文）

===== Evaluation
Each Submission has an estimated **Skill Rating** which is modeled by a Gaussian \\(\mathcal N (\mu, \sigma^2)\\) where \\(\mu\\) is the estimated skill and \\(\sigma\\) represents our uncertainty of that estimate.

When you upload a Submission, we first play a **Validation Episode** where that Submission plays against itself to make sure it works properly.  If the Episode fails, the Submission is marked as Error.  Otherwise, we initialize the Submission with \\(\mu_0 = 600\\) and it joins the pool of All Submissions for ongoing evaluation.

We repeatedly run Episodes from the pool of All Submissions, and try to pick Submissions with similar ratings for fair matches.  We aim to run ~8 Episodes a day per Submission, with an additional slight rate increase for newer Episodes to give you feedback faster.

After an Episode finishes, we'll update the Rating estimate for both Submissions.  If one Submission won, we'll increase its \\(\mu\\) and decrease its opponent's \\(\mu\\) -- if the result was a draw, then we'll move the two \\(\mu\\) values closer towards their mean.  The updates will have magnitude relative to the deviation from the expected result based on the previous \\(\mu\\) values, and also relative to each Submission's uncertainty \\(\sigma\\).  We also reduce the \\(\sigma\\) terms relative to the amount of information gained by the result.

So all valid Submissions will continually play more matches and have dynamically changing scores as the pool increases.  The Leaderboard will show the \\(\mu\\) value of each Team's best Submission.
===== Environment Rules
## Episode Objective

Use your Agent to get a certain number of your checkers in a row horizontally, vertically, or diagonally on the game board before your opponent.

## How To Play

Player 1 will take the first turn. When it's your turn, you add, or “drop”, one of your checkers into the top of a column on the board and the checker will land in the last empty row in that column. The following can occur after dropping your checker in a column:

1. If the column you chose has no empty rows or is out of range of the number of columns, you lose the episode.
2. If the checker placed creates an "X-in-a-row", you win the episode. X represents the number specified in the parameters, for example 4, and to be “in a row”, the checkers can be in a row horizontally vertically, or diagonally.
3. If there are no empty cells, you tie the episode.
4. Otherwise, it's your opponent’s turn.

This episode continues until a win, lose, or tie occurs.

## Writing Agents

An Agent will receive the following parameters:

1. The episode configuration:
    1. Number of Columns on the board.
    2. Number of Rows on the board.
    3. How many checkers, X, "in a row" are required to win.
2. The current state of the board (serialized grid of cells; rows by cols).
    1. Empty cells are represented by "0".
    2. Player 1's checkers are represented by "1".
    3. Player 2's checkers are represented by "2".
3. Which player you are ("1" or "2").

An Agent should return which column to place a checker in.  The column is an integer: [0, configuration.columns), and represents the columns going left to right. The row is an integer: [0, configuration.rows), and represents the rows going top to bottom

Here’s what that looks like as code: 

```python
def agent(observation, configuration):
    # Number of Columns on the Board.
    columns = configuration.columns
    # Number of Rows on the Board.
    rows = configuration.rows
    # Number of Checkers "in a row" needed to win.
    inarow = configuration.inarow
    # The current serialized Board (rows x columns).
    board = observation.board
    # Which player the agent is playing as (1 or 2).
    mark = observation.mark

    # Return which column to drop a checker (action).
    return 0
```

## Agent Rules

1. Your Submission must be an “Agent”.
2. An Agent may only use any module from the Kaggle Kernels notebook image.
3. An Agent’s sole purpose is to generate an action. Activities/code which do not directly contribute to this will be considered malicious and handled according to the Rules.
4. An Agent can have a maximum file size limit of 100 MB.
5. An Agent must return an action within 2 seconds (60 seconds on the first turn) of being invoked. If the Agent does not, it will lose the episode and may be invalidated.
6. An Agent which throws errors or returns an invalid action will lose the episode and may be invalidated.

