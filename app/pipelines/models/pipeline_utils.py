from app.projects.models import NEW_CODE_TAG, PIPELINE_START_TAG, PIPELINE_END_TAG


async def get_file_lines(file_path):
    """
    Returns the lines contained in the file at file_path

    => Returns a list of lines; if the line(s) is an action, it is represented as a tuple (action_id, line)
    """
    lines = []
    with open(file_path, 'r') as file:
        in_pipeline = False
        action_id = 0
        temp_action_lines = "" # Enables to deal with multi-line actions
        for line in file.readlines():
            if PIPELINE_START_TAG in line:
                lines.append(line)
                in_pipeline = True
            elif PIPELINE_END_TAG in line:
                lines.append(line)
                in_pipeline = False
            elif in_pipeline and NEW_CODE_TAG not in line and line.strip() != "":
                if "#sq_action:" not in line:
                    temp_action_lines += line
                    continue
                else:
                    temp_action_lines += line
                    lines.append((action_id, temp_action_lines))
                    temp_action_lines = ""
                    action_id += 1
            else:
                lines.append(line)
    return lines
