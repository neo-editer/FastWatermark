import os
import subprocess
import FreeSimpleGUI as sg
import ffmpeg

def get_available_vcodec():
    try:
        # Check if NVIDIA GPU is available
        result = subprocess.run(['ffmpeg', '-hwaccels'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if 'nvenc' in result.stdout:
            return 'h264_nvenc'
        
        # Check if Intel GPU is available
        if 'qsv' in result.stdout:
            return 'h264_qsv'
        
        # Fallback to x264 if no hardware acceleration available
        return 'libx264'
    except Exception as e:
        print(f"Error checking available codecs: {e}")
        return 'libx264'

def add_watermark(input_video, watermark, position='top-left', duration=None, start_time=0, scale_factor=1):
    # Define the position of the watermark
    positions = {
        'top-left': {'x': 10, 'y': 10},
        'top-right': {'x': 'main_w-overlay_w-10', 'y': 10},
        'bottom-left': {'x': 10, 'y': 'main_h-overlay_h-10'},
        'bottom-right': {'x': 'main_w-overlay_w-10', 'y': 'main_h-overlay_h-10'},
        'center': {'x': '(main_w-overlay_w)/2', 'y': '(main_h-overlay_h)/2'}
    }
    
    if position not in positions:
        raise ValueError("Invalid position. Choose from 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'.")

    pos = positions[position]
    
    # Convert start_time and duration to integers
    start_time = int(start_time) if start_time else 0
    duration = int(duration) if duration else None
    
    # Prepare paths for the output file
    output_video = os.path.splitext(input_video)[0] + '_watermark.mp4'

    # Get the available video codec
    vcodec = get_available_vcodec()

    # Get video dimensions
    probe = ffmpeg.probe(input_video)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        raise RuntimeError("No video stream found in the input file.")
    video_width = video_stream['width']
    video_height = video_stream['height']

    # Check if audio stream exists
    has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
    
    # Define scale factors
    scale_factors = [1, 1/1.2, 1/1.5, 1/2, 1/2.5]  # Scale factors for 1 to 5
    scale_width = int(video_width * scale_factors[scale_factor - 1])
    scale_height = int(video_height * scale_factors[scale_factor - 1])
    
    # Build the ffmpeg input and overlay filters
    video_input = ffmpeg.input(input_video)
    watermark_input = ffmpeg.input(watermark).filter('scale', scale_width, -1)  # Maintain aspect ratio
    
    if duration:
        watermark_input = watermark_input.filter('setpts', f'PTS-STARTPTS+{start_time}/TB').filter('trim', start=start_time, duration=duration)
        overlay_filter = ffmpeg.overlay(video_input, watermark_input, x=pos['x'], y=pos['y'], enable=f'between(t,{start_time},{start_time + duration})')
    else:
        overlay_filter = ffmpeg.overlay(video_input, watermark_input, x=pos['x'], y=pos['y'])
    
    # Use the detected vcodec for hardware acceleration or fallback to x264
    output_args = {'vcodec': vcodec, 'pix_fmt': 'yuv420p'}
    if has_audio:
        output_args.update({'acodec': 'aac', 'audio_bitrate': '192k'})
        ffmpeg.output(overlay_filter, video_input.audio, output_video, **output_args).run(overwrite_output=True)
    else:
        ffmpeg.output(overlay_filter, output_video, **output_args).run(overwrite_output=True)

def main():
    # Define the layout of the window
    layout = [
        [sg.Text('Select a video file:')],
        [sg.Input(key='-FILE-', enable_events=True), sg.FileBrowse(file_types=(("Video Files", "*.mp4;*.avi;*.mov"),))],
        [sg.Text('Select a watermark image file:')],
        [sg.Input(key='-WATERMARK-', enable_events=True), sg.FileBrowse(file_types=(("Image Files", "*.png;*.jpg"),))],
        [sg.Text('Choose watermark position:')],
        [sg.Combo(['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'], key='-POSITION-', default_value='top-left')],
        [sg.Text('Show watermark for (seconds), leave blank for full video:')],
        [sg.Input(key='-DURATION-', size=(10, 1))],
        [sg.Text('Start time (seconds), leave blank for start (default 0):')],
        [sg.Input(key='-START_TIME-', size=(10, 1))],
        [sg.Text('Watermark size (1 = Biggest 5 = Smallest):')],
        [sg.Combo([1, 2, 3, 4, 5], key='-SCALE-', default_value=1)],
        [sg.Button('Apply Watermark'), sg.Button('Cancel')],
        [sg.Text('', key='-OUTPUT-', size=(60, 2))]
    ]

    # Create the window
    window = sg.Window('Fast Watermark', layout)

    # Event loop
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        if event == 'Apply Watermark':
            file_path = values['-FILE-']
            watermark_path = values['-WATERMARK-']
            position = values['-POSITION-']
            duration = values['-DURATION-']
            start_time = values['-START_TIME-']
            scale_factor = int(values['-SCALE-'])

            if not file_path or not watermark_path:
                window['-OUTPUT-'].update('Please select both video and watermark files.')
                continue

            start_time = int(start_time) if start_time else 0
            duration = int(duration) if duration else None

            output_video = os.path.splitext(file_path)[0] + '_watermark.mp4'

            if os.path.exists(output_video):
                # Show confirmation dialog
                confirm = sg.popup_yes_no(f'The file "{output_video}" already exists. Do you want to replace it?')
                if confirm == 'No':
                    continue  # Skip the processing if the user does not want to replace the file

            output_message = (f'Selected video: {file_path}\n'
                              f'Selected watermark: {watermark_path}\n'
                              f'Position: {position}\n'
                              f'Duration: {duration if duration else "full video"}\n'
                              f'Start Time: {start_time}\n'
                              f'Scale Factor: {scale_factor}')
            window['-OUTPUT-'].update(output_message)

            try:
                # Call the add_watermark function
                add_watermark(file_path, watermark_path, position, duration, start_time, scale_factor)
                window['-OUTPUT-'].update(f'Watermark applied successfully. Output saved as: {output_video}')
            except Exception as e:
                window['-OUTPUT-'].update(f'Error: {str(e)}')

    # Close the window
    window.close()

if __name__ == "__main__":
    main()
