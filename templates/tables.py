from flask_table import Table, Col, LinkCol

class Results(Table):
    emp_id = Col('Employee Id')
    first_name = Col('First Name')
    last_name = Col('Last Name')
    location = Col('Location')
    pri_skill = Col('Primary Skill')
    image = Col('Profile Image')
    # delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='user_id'))