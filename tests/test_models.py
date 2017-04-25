#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest

from movieapp.models import db, User

create_user = False



class TestModels:
    def test_user_save(self):
        """ Test Saving the user model to the database """

        admin = User('admin', 'supersafepassword', 23, "14242", "student")
        db.session.add(admin)
        db.session.commit()

        user = User.query.filter_by(username="admin").first()
        assert user is not None

    def test_user_password(self):
        """ Test password hashing and checking """

        admin = User('admin', 'supersafepassword', 23, "14242", "student")

        assert admin.username == 'admin'
        assert admin.check_password('supersafepassword')