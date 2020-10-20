import { Box, Flex } from "@chakra-ui/core";
import { Text } from "@chakra-ui/core";

const Card = (props) => {

    var color;
    var emoji;
    
    switch(props.place){
        case 'first':
            color = "#FFD700";
            emoji = <span role="medal">🥇</span>;
            break;
        case 'second':
            color = "#D7D7D7";
            emoji = <span role="medal">🥈</span>;
            break;
        case 'third':
            color = "#A77044";
            emoji = <span role="medal">🥉</span>;
            break;
    }

    return (
      <Flex flexDirection="column" flexWrap="nowrap" alignSelf="stretch" flex="1 1" h="600px" m="15px" padding="15px" backgroundColor={color} rounded="lg" overflow="hidden">
        <Text display="flex" color="black" mt="1" fontWeight="semibold" as="h2">
            {emoji}<span>{props.name}</span>
        </Text>
        <Box minH="250px" backgroundPosition={["","","",""]} rounded="lg" w="100%" padding="10px" backgroundRepeat="no-repeat" backgroundSize="cover" backgroundPosition="center" backgroundImage={"url(" + props.img + ")"}/>
        <Flex paddingTop="25px" justifyContent="center" flexDirection="column">
            <Text wordBreak="break-word" mt="10" fontWeight="300" as="h3"><strong>Участници: </strong>{props.teammates}</Text>
            <Text wordBreak="break-word" mt="10" fontWeight="300" as="h3"><strong>Проект: </strong>{props.project}</Text>
        </Flex>
      </Flex>
    );
}

export default Card;