import { Editor } from "@toast-ui/react-editor";
import ExitImg from "assets/img/exit.svg";
import WriteLayout from "components/layouts/WriteLayout";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Col, Form, Image, Row } from "react-bootstrap";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuthStore } from "stores/RootStore";
import { customAxios } from "util/CustomAxios";

const UpdatePost = () => {
  const refs = useRef({
    title: null,
    /** @type {Editor} editor */
    editor: null,
  });

  const authStore = useAuthStore();
  const navigate = useNavigate();
  const { postIdx } = useParams();

  const [editorHeight, setEditorHeight] = useState(0);

  const getPost = useCallback(() => {
    customAxios
      .privateAxios({
        method: `get`,
        url: `/api/v1/posts/${postIdx}?update=true`,
      })
      .then((response) => {
        if (response.status === 200) {
          refs.current.title.value = response.data.content.title;
          refs.current.editor
            .getInstance()
            .setMarkdown(response.data.content.content);
        } else {
          alert(response.data.message);
        }
      })
      .catch((error) => {
        if (error?.response?.data?.detail != null) {
          alert(JSON.stringify(error?.response?.data?.detail));
        } else if (error?.response?.data?.message != null) {
          alert(error.response.data.message);
        } else {
          alert("오류가 발생했습니다. 관리자에게 문의하세요.");
        }
      })
      .finally(() => {});
  }, [postIdx]);

  useEffect(() => {
    setEditorHeight(`${window.innerHeight - 190}px`);
    window.onresize = () => setEditorHeight(`${window.innerHeight - 190}px`);
  }, []);

  useEffect(() => {
    if (isNaN(postIdx)) {
      alert("잘못된 접근입니다.");
      navigate("/", { replace: true });
      return;
    }

    if (authStore.loginUser === null) {
      alert("로그인이 필요합니다.");
      navigate("/login", { replace: true });
    } else if (authStore.loginUser !== undefined) {
      getPost();
    }
  }, [authStore, navigate, postIdx, getPost]);

  return (
    <WriteLayout>
      <Row>
        <Col>
          <Form.Control
            ref={(el) => (refs.current.title = el)}
            className="border-0 w-100 fs-1 mt-3 mb-3"
            type="text"
            placeholder="제목을 입력하세요"
          />
        </Col>
      </Row>
      <Editor
        ref={(el) => (refs.current.editor = el)}
        previewStyle="vertical"
        initialEditType="markdown"
        height={editorHeight}
      />
      <Row className="row fixed-bottom p-3 bg-white shadow-lg">
        <Col className="me-auto">
          <Link
            to={`/post/${postIdx}`}
            replace={true}
            className="text-decoration-none text-dark"
          >
            <Image src={ExitImg} />
            <span className="m-2">나가기</span>
          </Link>
        </Col>
        <Col className="col-auto">
          <Button
            className="btn-light fw-bold text-white"
            type="button"
            style={{ backgroundColor: "#20c997" }}
          >
            수정하기
          </Button>
        </Col>
      </Row>
    </WriteLayout>
  );
};

export default UpdatePost;
