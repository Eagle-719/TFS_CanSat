# TFS_CanSat
Contains all code and design for electronics and ground station

The ground station:
- The C# application connects to the COM port, reads, checks data, appends to adatok.txt
- The apache server creates a local visualization, allows the interface to send target coordinates and frequency changes, and sends to web server
- the web server receives, visualizes, is publically accessible, but does not allow interference.

Under dev.:
- php send adress to be decided
- temperature and pressure graphs in visualization
- interface and resend are under devlopment
