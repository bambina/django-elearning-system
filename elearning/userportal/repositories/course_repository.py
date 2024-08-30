from userportal.models import TeacherProfile


class CourseRepository:
    @staticmethod
    def fetch_teacher_courses(teacher: TeacherProfile):
        return teacher.courses.all()
