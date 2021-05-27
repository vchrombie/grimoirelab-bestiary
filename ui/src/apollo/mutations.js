import gql from "graphql-tag";

const ADD_PROJECT = gql`
  mutation addProject(
    $ecosystemId: ID
    $name: String
    $title: String
    $parentId: ID
  ) {
    addProject(
      ecosystemId: $ecosystemId
      name: $name
      title: $title
      parentId: $parentId
    ) {
      project {
        id
        name
      }
    }
  }
`;

const DELETE_PROJECT = gql`
  mutation deleteProject($id: ID) {
    deleteProject(id: $id) {
      project {
        id
      }
    }
  }
`;

const MOVE_PROJECT = gql`
  mutation moveProject($fromProjectId: ID, $toProjectId: ID) {
    moveProject(fromProjectId: $fromProjectId, toProjectId: $toProjectId) {
      project {
        id
        name
      }
    }
  }
`;

const UPDATE_PROJECT = gql`
  mutation updateProject($data: ProjectInputType, $id: ID) {
    updateProject(data: $data, id: $id) {
      project {
        id
        name
      }
    }
  }
`;

const addProject = (apollo, data) => {
  const response = apollo.mutate({
    mutation: ADD_PROJECT,
    variables: {
      ecosystemId: data.ecosystemId,
      name: data.name,
      title: data.title,
      parentId: data.parentId
    }
  });
  return response;
};

const deleteProject = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_PROJECT,
    variables: {
      id: id
    }
  });
  return response;
};

const moveProject = (apollo, fromProjectId, toProjectId) => {
  const response = apollo.mutate({
    mutation: MOVE_PROJECT,
    variables: {
      fromProjectId: fromProjectId,
      toProjectId: toProjectId
    }
  });
  return response;
};

const updateProject = (apollo, data, id) => {
  const response = apollo.mutate({
    mutation: UPDATE_PROJECT,
    variables: {
      data: data,
      id: id
    }
  });
  return response;
};

export { addProject, deleteProject, moveProject, updateProject };
