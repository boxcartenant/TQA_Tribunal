# TQA_Tribunal
Tribunal Bot

This is a discord bot for the TQ&A forum.

It's been through a lot of revisions because of changes to discord libraries, changes from token to slash commands, and changes to the hosting server. Consequently, it's looking a little sloppy at the moment.

The Tribunal Bot provides definitions for the roles in TQ&A, and keeps a record of mock trials.
These are the commands for general use:

- /define - get the definition for a role.
- /triallist - See a summary list of trials.
- /trialrecord - See the full record for one trial.
- /accuse - Initiate a case by accusing someone of a crime.
- /witness - Submit evidence for an accusation. Only cases with two witnesses go to trial.
- /defense - Submit defense for a trial.
- /fortherecord - Make a note on a trial.
- /plea - Defendant only: state innocent or guilty.
- /forgive - Accuser only: delete the trial and accusation before penalty.
- /execute - Accuser only: after penalty has been issued, cast the first stone.

These are the commands for judges:

- /reject - Delete an accusation before it goes to trial.
- /starttrial - Accept a case and register yourself as the acting judge for it.
- /judge - State guilty or innocent for the record (does not close the case).
- /consult - Request help from other judges, or provide help to the acting judge.
- /penalize - Finalize a case by deciding the penalty. The right to execute the penalty is deferred to the accuser by default, but can be set to trigger immediately by the judge.
- /penalties - Show the list of penalties with some brief explanations.

Known bugs:
- Right now, none of the penalties are working, because of some kind of unicode error associated with the serialize function for dumping data into the "replit" db.
- Clean up the code and verify accuracy of the comments.

Feature wishlist:
- /close - to delete dead cases
- /trialsummary - to show like a formal court case summary or something
- /welcome - to output Isaiah 14:9
