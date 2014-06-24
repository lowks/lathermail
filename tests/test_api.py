# -*- coding: utf-8 -*-
import datetime
from tests.utils import BaseTestCase, smtp_send_email, prepare_send_to_field


class ApiTestCase(BaseTestCase):

    def test_send_and_search(self):
        to = [("Rcpt1", "rcpt1@example.com"), ("Rcpt2", "rcpt2@example.com"), ("", "rcpt3@example.com")]
        emails = [t[1] for t in to]
        to = prepare_send_to_field(to)
        n = 3
        body_fmt = u"you you привет {}"
        subject_fmt = u"Test subject хэллоу {}"
        file_content = "file content"
        for i in range(n):
            smtp_send_email(
                to, subject_fmt.format(i), u"Me <asdf@exmapl.com>", body_fmt.format(i),
                user=self.inbox, password=self.password, port=self.port, emails=emails,
                attachments=[(u"tасдest.txt", file_content)]
            )
        res = self.get("/").json
        self.assertEquals(res["message_count"], n)

        msg = res["message_list"][0]
        self.assertEquals(len(msg["parts"]), 2)
        self.assertEquals(msg["parts"][0]["body"], body_fmt.format(n - 1))
        self.assertEquals(msg["parts"][0]["is_attachment"], False)
        self.assertEquals(msg["parts"][1]["body"], file_content)
        self.assertEquals(msg["parts"][1]["is_attachment"], True)

        def msg_count(params=None):
            return self.get("/", params=params).json["message_count"]

        self.assertEquals(msg_count({"subject": subject_fmt.format(0)}), 1)
        self.assertEquals(msg_count({"subject_contains": "Test"}), n)
        self.assertEquals(msg_count({"subject_contains": "no such message"}), 0)

        before_send = datetime.datetime.now().isoformat()
        smtp_send_email("test1@example.com", "test", "me@example.com", "Hello",
                        user=self.inbox, password=self.password, port=self.port)

        self.assertEquals(msg_count({"recipients.address": emails[0]}), n)
        self.assertEquals(msg_count({"recipients.name": "Rcpt1"}), n)

        self.assertEquals(msg_count({"recipients.address": "no_such_email@example.com"}), 0)
        now = datetime.datetime.now().isoformat()
        self.assertEquals(msg_count({"created_at_lt": before_send}), n)
        self.assertEquals(msg_count({"created_at_gt": before_send}), 1)
        self.assertEquals(msg_count({"created_at_lt": now}), n + 1)
        self.assertEquals(msg_count({"created_at_gt": now}), 0)

    def test_different_boxes_and_deletion(self):
        password1 = "inbox1"
        password2 = "inbox2"
        user = "user"
        n = 5

        def message_count(user, password):
            return self.get("/", headers=auth(user, password)).json["message_count"]

        for i in range(n):
            self.send(user, password1)
            self.send(user, password2)

        self.assertEquals(message_count(user, password1), n)
        self.assertEquals(message_count(user, password2), n)

        one_message = self.get("/", headers=auth(user, password1)).json["message_list"][0]
        self.delete("/{}".format(one_message["_id"]), headers=auth(user, password1))
        self.assertEquals(
            self.delete("/{}".format(one_message["_id"]),
                        headers=auth(user, password1), raise_errors=False).status_code,
            404
        )
        self.assertEquals(message_count(user, password1), n - 1)
        self.delete("/", headers=auth(user, password1))
        self.assertEquals(message_count(user, password1), 0)

        n_new = 2
        new_subject = "new subject"
        for i in range(n_new):
            self.send(user, password2, subject=new_subject)

        self.assertEquals(message_count(user, password2), n + n_new)
        self.delete("/", headers=auth(user, password2), params={"subject": new_subject})
        self.assertEquals(message_count(user, password2), n)

    def test_read_flag(self):
        n_read = 5
        n_unread = 3
        subject_read = "read emails"
        subject_unread = "unread emails"

        for i in range(n_read):
            self.send(subject=subject_read)
        for i in range(n_unread):
            self.send(subject=subject_unread)

        self.assertEquals(self.get("/", {"subject": subject_read}).json["message_count"], n_read)
        self.assertEquals(self.get("/", {"read": False}).json["message_count"], n_unread)
        self.assertEquals(self.get("/", {"read": False}).json["message_count"], 0)
        self.assertEquals(self.get("/").json["message_count"], n_unread + n_read)


def auth(user, password):
    return {"X-Mail-Inbox": user, "X-Mail-Password": password}
