import "@toast-ui/editor/dist/toastui-editor.css";
import { Editor } from "@toast-ui/react-editor";
import ExitImg from "assets/img/exit.svg";
import WriteLayout from "components/layouts/WriteLayout";
import { useEffect, useRef, useState, useCallback } from "react";
import { Button, Col, Form, Image, Row } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "stores/RootStore";
import { customAxios } from "util/CustomAxios";
const InsertPost = () => {
  const refs = useRef({
    title: null,
    /** @type {Editor} editor */
    editor: null,
  });

  const authStore = useAuthStore();
  const navigate = useNavigate();
  const [editorHeight, setEditorHeight] = useState(0);

  const [editorImage, setEditorImage] = useState([]); // 이전 에디터 내용 저장

  // 임시저장
  const tempPostSave = () => {
    const tempPost = {
      title: refs.current.title.value,
      content: refs.current.editor.getInstance().getMarkdown(),
    };
    localStorage.setItem("tempPost", JSON.stringify(tempPost));
    alert("임시저장되었습니다.");
  };

  // 임시저장 불러오기
  const tempPostCheck = () => {
    const tempPost = localStorage.getItem("tempPost");
    if (tempPost != null) {
      if (window.confirm("임시저장된 글이 있습니다. 불러오시겠습니까?")) {
        const parsedTempPost = JSON.parse(tempPost);
        refs.current.title.value = parsedTempPost.title;
        refs.current.editor.getInstance().setMarkdown(parsedTempPost.content);
      }
    } else {
      localStorage.removeItem("tempPost");
    }
  };

  // 유효성 체크
  const validateFields = () => {
    const title = refs.current.title.value;
    const content = refs.current.editor.getInstance().getMarkdown();

    if (title === "") {
      alert("제목을 입력하세요.");
      return false;
    }
    if (content === "") {
      alert("내용을 입력하세요.");
      return false;
    }

    return true;
  };

  // 게시하기
  const insertPost = () => {
    if (!validateFields()) {
      return;
    }

    const title = refs.current.title.value;
    const content = refs.current.editor.getInstance().getMarkdown();

    const markdownImageRegex = /\[.*?\]\((.*?)\)/gi;
    const markdownRegex = /(\*|_|#|`|~|>|!|\[|\]|\(|\)|\{|\}|\||\\)/gi;

    const summary = content
      .replace(markdownImageRegex, "")
      .replace(markdownRegex, "")
      .substring(0, 151);

    const imageList = content.match(markdownImageRegex);
    const imageArray = imageList ? imageList : [];

    const thumbnailMarkdown = imageArray.length > 0 ? imageArray[0] : null;

    const thumbnail =
      thumbnailMarkdown != null
        ? thumbnailMarkdown.substring(
            thumbnailMarkdown.indexOf("](") + 2,
            thumbnailMarkdown.length - 1
          )
        : null;

    const imageUploadList = [...new Set(imageArray)].map((image) => {
      return image.substring(image.indexOf("](") + 2, image.length - 1);
    });

    const newPost = {
      title: title,
      thumbnail: thumbnail,
      content: content,
      summary: summary,
      imageList: imageUploadList,
    };

    customAxios
      .privateAxios({
        method: `post`,
        url: `/api/v1/posts`,
        data: newPost,
      })
      .then((response) => {
        if (response.status === 201) {
          alert("게시하였습니다.");
          localStorage.removeItem("tempPost");
          navigate(`/post/${response.data.content.idx}`, { replace: true });
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
      });
  };

  useEffect(() => {
    if (authStore.loginUser != null) {
      refs.current.editor.getInstance().setMarkdown("");
      setEditorHeight(`${window.innerHeight - 190}px`);
      window.onresize = () => setEditorHeight(`${window.innerHeight - 190}px`);
      tempPostCheck();
    }
  }, [authStore]);

  // 에디터 내용 변경 감지
  const handleEditorChange = useCallback(() => {
    const currentContent = refs.current.editor.getInstance().getMarkdown();
    const markdownImageRegex = /!\[.*?\]\((.*?)\)/g;
    const newImages = currentContent.match(markdownImageRegex) || [];

    setEditorImage(newImages);
  }, []);

  const exitEditor = () => {
    if (window.confirm("작성 중인 내용이 저장되지 않습니다. 나가시겠습니까?")) {
      // 사용자 확인 후에만 이미지 삭제 시도
      console.log("이미지 목록:", editorImage);
      if (editorImage.length > 0) {
        removeImagesFromServer(editorImage);
      }

      // 에디터 페이지를 나감
      navigate(0);
    }
  };

  // 서버에 이미지 삭제 요청
  const removeImagesFromServer = (removeImages) => {
    removeImages = removeImages.map((image) => {
      return (
        "static/" +
        image
          .substring(image.indexOf("](") + 2, image.length - 1)
          .replace(/\\/g, "/")
          .split("/static/")[1]
      );
    });
    console.log("삭제할 이미지 목록:", removeImages);
    // 이미지 경로를 추출하고 유효성 체크
    if (removeImages.length > 0) {
      // 여러 이미지를 한 번에 삭제하는 방식
      customAxios
        .privateAxios({
          method: "delete",
          url: `/api/v1/images/exit/editorImage`, // 여러 이미지 삭제 API로 수정
          params: { imagePaths: removeImages }, // 배열로 전송
        })
        .then((response) => {
          if (response.status === 200) {
            console.log("이미지가 성공적으로 삭제되었습니다");
          } else {
            console.error("이미지 삭제 실패:", response.data.message);
          }
        })
        .catch((error) => {
          console.error("이미지 삭제 오류:", error);
        });
    } else {
      console.log("삭제할 이미지가 없습니다.");
    }
  };

  useEffect(() => {
    if (refs.current.editor) {
      refs.current.editor.getInstance().on("change", handleEditorChange);
    }
  }, [handleEditorChange]);

  const imageUploadHandler = (blob, callback) => {
    const formData = new FormData();
    formData.append("image", blob);

    customAxios
      .privateAxios({
        method: `post`,
        url: `/api/v1/images/upload`,
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        if (response.status === 201) {
          const fileName = response.data.content.fileName;
          const imageUrl = response.data.content.url;

          callback(imageUrl, fileName);
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
      });
  };

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
        hooks={{
          addImageBlobHook: (blob, callback) => {
            imageUploadHandler(blob, callback);
          },
        }}
      />
      <Row className="row fixed-bottom p-3 bg-white shadow-lg">
        <Col className="me-auto">
          <Link
            to={-1}
            onClick={exitEditor}
            className="text-decoration-none text-dark"
          >
            <Image src={ExitImg} />
            <span className="m-2">나가기</span>
          </Link>
        </Col>
        <Col className="col-auto">
          <Button
            className="btn-light fw-bold"
            type="button"
            onClick={tempPostSave}
          >
            임시저장
          </Button>
        </Col>
        <Col className="col-auto">
          <Button
            className="btn-light fw-bold text-white"
            type="button"
            style={{ backgroundColor: "#20c997" }}
            onClick={insertPost}
          >
            게시하기
          </Button>
        </Col>
      </Row>
    </WriteLayout>
  );
};

export default InsertPost;
