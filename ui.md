"I need to build a modern desktop user interface (GUI) for an OBS stream automation tool. Please use Python with the customtkinter library. The application must feature a strict Dark Mode theme with rounded corners for all panels, buttons, and input fields.

The layout must be structurally divided into three main vertical columns:

1. Left Column (Tools Panel):

A vertical panel titled 'Tools'.

Contains 4 selectable toggle buttons (functioning like a radio group where only one is active/highlighted at a time):

'123 numbers'

'ABC Text'

'Gradient' (include a visual cue or icon of a gradient)

'Pixel' (include a visual cue or icon of a checkerboard)

2. Center Column (Main Workspace):
This is the widest column, taking up most of the screen, and is split vertically into three sections:

Top Row (Connection Header): Contains connection settings. A row with the label 'OBS ws', a dropdown menu for IP addresses, a 'PORT' text input, and a green circular 'State' indicator. Below that, a row with the label 'Spoutsenders', a dropdown menu, and another green circular 'State' indicator.

Middle Row (Video Canvas): A large, prominent, pure black rectangular frame. This represents the live video feed area where bounding boxes will be drawn.

Bottom Row (JSON Viewer): A dark panel titled 'Json' that displays a block of formatted, syntax-highlighted JSON code (read-only text box).

3. Right Column (Properties Panel):

A vertical panel titled 'properties'.

Top Section (Coordinates): Two text entry fields labeled 'X' and 'Y'.

Bottom Section (Actions): Titled 'Actions'. It contains:

A 'Source' dropdown menu.

A 'Filter' row containing a checkbox next to a dropdown menu.

An 'Action' section with a dropdown menu containing options like: 'Visibility: on', 'Off', 'Boolean'.

Please generate the complete, runnable Python code for this layout, ensuring the UI is responsive and well-padded."