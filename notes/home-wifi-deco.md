# Home Wi-Fi: TP-Link Deco X10 setup (paused 20 Oct 2026, pick up later)

Hardware: 2 × TP-Link Deco X10 (EU), AX1500 Wi-Fi 6 mesh. Internet: MEO fibre (MEO "Fibergateway" box stays: it terminates the fibre and runs MEO TV + phone).
Marco is fine with two routers (Deco in Router mode, double NAT). Access Point mode is the cleaner alternative.

## Key fact (the question Marco asked)
Deco is MESH, not an extender. It cannot join MEO's Wi-Fi.
- Deco #1 MUST be cabled (Ethernet) to a LAN port on the MEO box. That cable is its internet.
- Deco #2 connects wirelessly to Deco #1 and is the one that carries Wi-Fi to the other floor.
- To put Deco #1 itself on another floor: long Ethernet cable (up to 100 m), wall Ethernet sockets, or a powerline adapter pair (~€40–60).

## Steps
1. Install the Deco app, log in with a TP-Link ID. Bluetooth + location on.
2. If a unit was used before: paperclip in RESET 2–5 s until it blinks yellow; wait for pulsing blue.
3. Deco #1: Ethernet to MEO box LAN port → power → pulsing blue → app "+ → Deco X10" → connection type Dynamic IP → set Wi-Fi name/password → solid white.
4. Deco #2: app "+ → Add Deco" → place halfway to the weak area (≤2 rooms / 1 floor away, raised, in the open) → solid white.
5. Firmware: More → System → Update Deco.
6. Wi-Fi clash: give the Deco a different name from MEO's, OR turn off MEO Wi-Fi (http://192.168.1.254, admin login on the box sticker, or ask MEO support 16200).
   Trick: if the Deco uses the SAME name + password as MEO and MEO's Wi-Fi is then turned off, every device reconnects by itself.
7. Leave MEO TV boxes plugged into the MEO box. Don't ask MEO for bridge mode (can break TV/phone).
8. Optional: Access Point mode = More → Advanced → Operation Mode. It turns off parental controls / HomeShield / QoS.

## Light colours
yellow = booting/resetting · pulsing blue = ready for setup · solid blue = setting up · solid white = OK · pulsing red = too far from Deco #1 · solid red = no internet
