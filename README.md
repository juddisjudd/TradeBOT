# Trading Bot for Discord
This is a Discord bot designed to help users coordinate trading items in a video game.

## Features
- Users can initiate trades with other users using the **!starttrade** command.
- Temporary channels are created for users to discuss and complete their trades.
- Users can mark their trade as complete with the **!complete** command.
- After completing a trade, users can rate each other using the **!rate** command.
- Users can check their reputation using the **!check** command.

## Usage
1. Initiate a trade with another user:
```css
!starttrade @User
```
2. Accept or decline the trade by reacting with 👍 or 👎.
3. If both parties agree to the trade, a temporary channel will be created.
4. When the trade is complete, both users must use the !complete command.
5. After completing the trade, users are prompted to rate each other with the !rate command:
```css
!rate @User
```
Check the reputation of a user:
```css
!check @User
```
