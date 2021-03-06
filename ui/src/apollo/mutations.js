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

const ADD_ECOSYSTEM = gql`
  mutation addEcosystem($name: String!, $title: String, $description: String) {
    addEcosystem(name: $name, title: $title, description: $description) {
      ecosystem {
        id
      }
    }
  }
`;

const UPDATE_ECOSYSTEM = gql`
  mutation updateEcosystem($data: EcosystemInputType, $id: ID) {
    updateEcosystem(data: $data, id: $id) {
      ecosystem {
        id
      }
    }
  }
`;

const DELETE_ECOSYSTEM = gql`
  mutation deleteEcosystem($id: ID!) {
    deleteEcosystem(id: $id) {
      ecosystem {
        id
      }
    }
  }
`;

const TOKEN_AUTH = gql`
  mutation tokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
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

const addEcosystem = (apollo, data) => {
  const response = apollo.mutate({
    mutation: ADD_ECOSYSTEM,
    variables: {
      name: data.name,
      title: data.title,
      description: data.description
    }
  });
  return response;
};

const updateEcosystem = (apollo, data, id) => {
  const response = apollo.mutate({
    mutation: UPDATE_ECOSYSTEM,
    variables: {
      data: data,
      id: id
    }
  });
  return response;
};

const deleteEcosystem = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_ECOSYSTEM,
    variables: {
      id: id
    }
  });
  return response;
};

const tokenAuth = (apollo, username, password) => {
  const response = apollo.mutate({
    mutation: TOKEN_AUTH,
    variables: {
      username: username,
      password: password
    }
  });
  return response;
};

export {
  addProject,
  deleteProject,
  moveProject,
  updateProject,
  addEcosystem,
  updateEcosystem,
  deleteEcosystem,
  tokenAuth
};
